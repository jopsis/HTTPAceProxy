#include "httpaceproxycpp/plugins.hpp"
#include "httpaceproxycpp/proxy.hpp"
#include "httpaceproxycpp/util.hpp"

#include <algorithm>
#include <filesystem>
#include <regex>
#include <sstream>
#include <thread>

namespace httpace {
namespace {

constexpr const char* kEpgUrl = "https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guiatv_sincolor0.xml.gz";
constexpr const char* kDefaultUserAgent = "curl/8.5.0";

std::string env_or(const char* name, const std::string& fallback) {
    const char* value = std::getenv(name);
    return value && *value ? std::string(value) : fallback;
}

// Cloudflare (ipfs.io) answers 403 to clients whose User-Agent claims to be a browser
// while their TLS/HTTP fingerprint does not match one, so the default is a plain
// non-browser agent. PLUGIN_USER_AGENT overrides it if a source ever needs another value.
const std::string& plugin_user_agent() {
    static const std::string agent = env_or("PLUGIN_USER_AGENT", env_or("HTTP_USER_AGENT", kDefaultUserAgent));
    return agent;
}

std::vector<std::string> env_csv_or(const char* name, const std::vector<std::string>& fallback) {
    const char* value = std::getenv(name);
    if (!value || !*value) return fallback;
    std::vector<std::string> out;
    for (auto item : split(value, ',', false)) {
        item = trim(item);
        if (!item.empty()) out.push_back(item);
    }
    return out.empty() ? fallback : out;
}

void send_bytes(ClientConnection& connection, int status, const std::string& content_type, const std::string& body,
                std::map<std::string, std::string> headers = {}) {
    headers["Content-Type"] = content_type;
    headers["Content-Length"] = std::to_string(body.size());
    headers["Connection"] = "close";
    connection.send_response_headers(status, status_reason(status), headers);
    connection.send_text(body);
}

std::string host_header(const RequestContext& ctx) {
    return ctx.request.header("host", "localhost:8888");
}

std::string normalize_github_blob_url(const std::string& url) {
    auto parsed = parse_url(url);
    if (parsed.host == "github.com" && parsed.path.find("/blob/") != std::string::npos) {
        return "https://raw.githubusercontent.com" + replace_all(parsed.path, "/blob/", "/");
    }
    return url;
}

bool is_shortener_url(const std::string& url) {
    auto host = lower(parse_url(url).host);
    if (starts_with(host, "www.")) host = host.substr(4);
    return host == "cutt.ly" || host == "urlfy.org" || host == "n9.cl" || host == "smurl.es";
}

std::string channel_name_from_request(const RequestContext& ctx) {
    auto base = ctx.parts.empty() ? "" : ctx.parts.back();
    return url_decode(basename_no_ext(base));
}

std::string ext_from_request(const RequestContext& ctx) {
    auto ext = extension_of(ctx.path);
    return ext.empty() ? "m3u8" : ext;
}

PlaylistItem item_from_m3u_extinf(const std::string& extinf_line, const std::string& url, const std::string& fallback_group = "Unknown") {
    auto attrs = parse_extinf_attrs(extinf_line);
    PlaylistItem item;
    item.name = parse_extinf_name(extinf_line);
    item.tvg = attrs.contains("tvg-name") ? attrs["tvg-name"] : item.name;
    item.tvgid = attrs.contains("tvg-id") ? attrs["tvg-id"] : "";
    item.group = attrs.contains("group-title") ? attrs["group-title"] : fallback_group;
    item.logo = attrs.contains("tvg-logo") ? attrs["tvg-logo"] : "";
    item.url = url;
    return item;
}

std::string normalize_catalog_name(std::string value, bool compact) {
    value = lower(value);
    value = std::regex_replace(value, std::regex(R"(^\d+(?:\.\d+)?\s*)"), "");
    value = std::regex_replace(value, std::regex(R"(\.w3u$)"), "");
    value = replace_all(value, "#", " ");
    std::map<std::string, std::string> aliases = {{"m", "movistar"}, {"tennis", "tenis"}, {"us", "usa"}};
    std::set<std::string> skip = compact ? std::set<std::string>{"sport", "sports", "tv", "channel", "hd", "newloop"} : std::set<std::string>{};
    std::vector<std::string> tokens;
    for (auto token : split(std::regex_replace(value, std::regex(R"([^a-z0-9]+)"), " "), ' ', false)) {
        if (aliases.contains(token)) token = aliases[token];
        if (!token.empty() && !skip.contains(token)) tokens.push_back(token);
    }
    return join(tokens, " ");
}

double rough_similarity(const std::string& a, const std::string& b) {
    if (a.empty() || b.empty()) return 0.0;
    auto a_tokens = split(a, ' ', false);
    auto b_tokens = split(b, ' ', false);
    std::set<std::string> aa(a_tokens.begin(), a_tokens.end());
    std::set<std::string> bb(b_tokens.begin(), b_tokens.end());
    std::size_t inter = 0;
    for (const auto& token : aa) if (bb.contains(token)) ++inter;
    auto score = static_cast<double>(inter * 2) / static_cast<double>(aa.size() + bb.size());
    std::size_t prefix = 0;
    auto limit = std::min(a_tokens.size(), b_tokens.size());
    while (prefix < limit && a_tokens[prefix] == b_tokens[prefix]) ++prefix;
    score += static_cast<double>(prefix) * 0.05;
    return std::min(1.0, score);
}

} // namespace

void RequestContext::rewrite_to(const std::string& new_path) {
    path = new_path;
    auto q = path.find('?');
    if (q != std::string::npos) {
        query = path.substr(q + 1);
        path = path.substr(0, q);
    }
    parts = split(path, '/', true);
    reqtype = parts.size() > 1 ? lower(parts[1]) : "";
    rewritten = true;
}

void PluginRegistry::add(std::shared_ptr<Plugin> plugin) {
    std::lock_guard<std::mutex> lock(mutex_);
    for (const auto& handler : plugin->handlers()) handlers_[lower(handler)] = plugin;
}

std::shared_ptr<Plugin> PluginRegistry::by_handler(const std::string& handler) const {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = handlers_.find(lower(handler));
    return it == handlers_.end() ? nullptr : it->second;
}

std::map<std::string, std::shared_ptr<Plugin>> PluginRegistry::handlers() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return handlers_;
}

std::vector<std::shared_ptr<Plugin>> PluginRegistry::unique_plugins() const {
    std::vector<std::shared_ptr<Plugin>> out;
    std::set<Plugin*> seen;
    std::lock_guard<std::mutex> lock(mutex_);
    for (const auto& [_, plugin] : handlers_) {
        if (seen.insert(plugin.get()).second) out.push_back(plugin);
    }
    return out;
}

PlaylistPlugin::PlaylistPlugin(Config config, HttpClient& http_client, std::string plugin_name,
                               std::string header, int update_minutes)
    : config_(std::move(config)),
      http_client_(http_client),
      plugin_name_(std::move(plugin_name)),
      header_(std::move(header)),
      update_minutes_(update_minutes),
      playlist_(header_) {
    playlist_time_ = std::chrono::steady_clock::time_point{};
    if (update_minutes_ > 0) {
        updater_ = std::thread([this] {
            while (!stop_updater_) {
                std::unique_lock<std::mutex> lock(updater_mutex_);
                if (updater_cv_.wait_for(lock, std::chrono::minutes(update_minutes_), [this] { return stop_updater_; })) break;
                lock.unlock();
                refresh_if_needed();
            }
        });
    }
}

PlaylistPlugin::~PlaylistPlugin() {
    {
        std::lock_guard<std::mutex> lock(updater_mutex_);
        stop_updater_ = true;
    }
    updater_cv_.notify_all();
    if (updater_.joinable()) updater_.join();
}

bool PlaylistPlugin::handle(RequestContext& ctx) {
    refresh_if_needed();
    if (ctx.path.find("/" + plugin_name_ + "/channel/") == 0) {
        if (!(ends_with(ctx.path, ".ts") || ends_with(ctx.path, ".m3u8"))) {
            send_bytes(ctx.connection, 404, "text/plain", "Invalid path: must end with .ts or .m3u8");
            return true;
        }
        return rewrite_channel(ctx, channel_name_from_request(ctx), ext_from_request(ctx));
    }
    {
        std::lock_guard<std::mutex> lock(mutex_);
        if (!etag_.empty() && etag_ == ctx.request.header("if-none-match")) {
            ctx.connection.send_response_headers(304, status_reason(304), {{"Connection", "close"}});
            return true;
        }
        auto body = playlist_.export_m3u(host_header(ctx), "/" + plugin_name_ + "/channel", ctx.query, true);
        std::map<std::string, std::string> headers = {{"Access-Control-Allow-Origin", "*"}};
        if (!etag_.empty() && ctx.request.version == "HTTP/1.1") headers["ETag"] = etag_;
        send_bytes(ctx.connection, 200, "audio/mpegurl; charset=utf-8", body, headers);
    }
    return true;
}

std::vector<PlaylistItem> PlaylistPlugin::playlist_items() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return playlist_.items();
}

std::map<std::string, std::string> PlaylistPlugin::channels() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return channels_;
}

std::map<std::string, std::string> PlaylistPlugin::picons() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return picons_;
}

std::size_t PlaylistPlugin::channel_count() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return channels_.size();
}

bool PlaylistPlugin::refresh_if_needed() {
    {
        std::lock_guard<std::mutex> lock(mutex_);
        auto age = std::chrono::steady_clock::now() - playlist_time_;
        if (!playlist_.empty() && age < std::chrono::minutes(30)) return true;
    }
    try { return refresh(); } catch (const std::exception& e) {
        log_line("ERROR", "[" + plugin_name_ + "] refresh failed: " + e.what());
        return false;
    }
}

void PlaylistPlugin::set_playlist(PlaylistGenerator playlist,
                                  std::map<std::string, std::string> channels,
                                  std::map<std::string, std::string> picons) {
    std::lock_guard<std::mutex> lock(mutex_);
    playlist_ = std::move(playlist);
    channels_ = std::move(channels);
    picons_ = std::move(picons);
    etag_ = playlist_.etag();
    playlist_time_ = std::chrono::steady_clock::now();
}

bool PlaylistPlugin::rewrite_channel(RequestContext& ctx, const std::string& channel_name, const std::string& ext) {
    std::string url;
    std::string icon;
    {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = channels_.find(channel_name);
        if (it == channels_.end()) {
            send_bytes(ctx.connection, 404, "text/plain", "[" + plugin_name_ + "] unknown channel: " + channel_name);
            return true;
        }
        url = it->second;
        icon = picons_.contains(channel_name) ? picons_[channel_name] : "";
    }
    auto parsed = parse_url(url);
    std::string new_path;
    if (parsed.scheme == "acestream") new_path = "/content_id/" + parsed.host + "/" + channel_name + "." + ext;
    else if (parsed.scheme == "infohash") new_path = "/infohash/" + parsed.host + "/" + channel_name + "." + ext;
    else if (parsed.scheme == "http" || parsed.scheme == "https") new_path = "/url/" + url_encode(url, "") + "/" + channel_name + "." + ext;
    else {
        send_bytes(ctx.connection, 404, "text/plain", "Unsupported channel URL scheme");
        return true;
    }
    ctx.channel_name = channel_name;
    ctx.channel_icon = icon;
    ctx.rewrite_to(new_path);
    return false;
}

class NewEraPlugin : public PlaylistPlugin {
public:
    NewEraPlugin(Config cfg, HttpClient& client)
        : PlaylistPlugin(std::move(cfg), client, "newera", PlaylistGenerator::epg_header(kEpgUrl, 0), 60) {}
protected:
    bool refresh() override {
        auto url = env_or("NEWERA_PLAYLIST_URL", "https://ipfs.io/ipns/k2k4r8lm8tkmuxbc8lkmq1in3v0oya1p6pe9o5bu0hu30br5ko08k2gb/data/listas/lista_iptv.m3u");
        auto response = http_client_.get(url, {{"User-Agent", plugin_user_agent()}}, 60);
        PlaylistGenerator playlist(header_);
        std::map<std::string, std::string> channels;
        std::map<std::string, std::string> picons;
        for (auto& item : parse_m3u_acestream_items(response.body, channels, picons)) {
            playlist.add_item(item);
        }
        if (channels.empty()) log_line("WARNING", "[newera] parsed zero channels from status " + std::to_string(response.status) + ", body bytes " + std::to_string(response.body.size()));
        set_playlist(std::move(playlist), std::move(channels), std::move(picons));
        log_line("INFO", "[newera] playlist generated with " + std::to_string(channel_count()) + " channels");
        return true;
    }
};

class ElcanoPlugin : public PlaylistPlugin {
public:
    ElcanoPlugin(Config cfg, HttpClient& client)
        : PlaylistPlugin(std::move(cfg), client, "elcano", PlaylistGenerator::epg_header(kEpgUrl, 0), 60) {}
protected:
    bool refresh() override {
        auto urls = env_csv_or("ELCANO_PLAYLIST_URL", {
            "https://ipfs.io/ipns/k51qzi5uqu5di462t7j4vu4akwfhvtjhy88qbupktvoacqfqe9uforjvhyi4wr/hashes_acestream.m3u",
            "https://ipfs.io/ipns/k51qzi5uqu5dh5qej4b9wlcr5i6vhc7rcfkekhrxqek5c9lk6gdaiik820fecs/hashes_acestream.m3u"
        });
        PlaylistGenerator playlist(header_);
        std::map<std::string, std::string> channels;
        std::map<std::string, std::string> picons;
        for (const auto& playlist_url : urls) {
            try {
                auto response = http_client_.get(playlist_url, {{"User-Agent", plugin_user_agent()}}, 60);
                for (auto& item : parse_m3u_acestream_items(response.body, channels, picons)) {
                    playlist.add_item(item);
                }
            } catch (const std::exception& e) {
                log_line("ERROR", "[elcano] source failed " + playlist_url + ": " + e.what());
            }
        }
        set_playlist(std::move(playlist), std::move(channels), std::move(picons));
        log_line("INFO", "[elcano] playlist generated with " + std::to_string(channel_count()) + " channels");
        return true;
    }
};

class AcePLPlugin : public PlaylistPlugin {
public:
    AcePLPlugin(Config cfg, HttpClient& client)
        : PlaylistPlugin(std::move(cfg), client, "acepl", PlaylistGenerator::epg_header("", 0), 30) {}
protected:
    bool refresh() override {
        auto response = http_client_.get("https://api.acestream.me/all?api_version=1.0&api_key=test_api_key", {{"User-Agent", plugin_user_agent()}}, 60);
        auto data = Json::parse(response.body);
        PlaylistGenerator playlist(header_, "#EXTINF:-1 group-title=\"{group}\" tvg-name=\"{name}\",{name}\n#EXTGRP:{group}\n{url}\n");
        std::map<std::string, std::string> channels;
        std::map<std::string, std::string> picons;
        for (const auto& channel : data.as_array()) {
            auto infohash = trim(channel["infohash"].as_string());
            auto name = trim(channel["name"].as_string());
            if (infohash.empty() || name.empty()) continue;
            PlaylistItem item;
            item.name = name;
            item.tvg = name;
            item.group = "Other";
            if (channel["categories"].is_array() && !channel["categories"].as_array().empty()) {
                std::vector<std::string> groups;
                for (const auto& cat : channel["categories"].as_array()) groups.push_back(cat.as_string());
                item.group = join(groups, ", ");
            }
            item.url = url_encode(name, "");
            item.availability = channel["availability"].as_number(0.0);
            channels[name] = "acestream://" + infohash;
            picons[name] = "";
            playlist.add_item(item);
        }
        set_playlist(std::move(playlist), std::move(channels), std::move(picons));
        log_line("INFO", "[acepl] playlist generated with " + std::to_string(channel_count()) + " channels");
        return true;
    }
};

class Af1c1onadosPlugin : public PlaylistPlugin {
public:
    Af1c1onadosPlugin(Config cfg, HttpClient& client)
        : PlaylistPlugin(std::move(cfg), client, "af1c1onados", PlaylistGenerator::epg_header(kEpgUrl, 0, true), 60) {}
protected:
    bool refresh() override {
        auto root_url = "https://raw.githubusercontent.com/af1Series1/Tritolgia/refs/heads/main/AcEStREAM%20iDs.w3u";
        auto data = fetch_playlist_json(root_url);
        PlaylistGenerator playlist(header_);
        std::map<std::string, std::string> channels;
        std::map<std::string, std::string> picons;
        collect_groups(data, "Others", playlist, channels, picons, {});
        set_playlist(std::move(playlist), std::move(channels), std::move(picons));
        log_line("INFO", "[af1c1onados] playlist generated with " + std::to_string(channel_count()) + " channels");
        return true;
    }

private:
    Json fetch_playlist_json(std::string url) {
        url = normalize_github_blob_url(url);
        if (is_shortener_url(url)) {
            try {
                auto response = http_client_.get(url, {{"User-Agent", plugin_user_agent()}}, 10, true);
                url = normalize_github_blob_url(response.url);
            } catch (...) {}
        }
        auto response = http_client_.get(url, {{"User-Agent", plugin_user_agent()}}, 20, true);
        return Json::parse(response.body);
    }

    std::optional<std::string> guess_catalog_url(const std::string& group_name) {
        try {
            auto strict = normalize_catalog_name(group_name, false);
            auto compact = normalize_catalog_name(group_name, true);
            double best_score = 0.0;
            double second_score = 0.0;
            std::string best_path;
            for (const auto& entry : catalog_entries()) {
                double score = std::max(rough_similarity(strict, entry.strict), rough_similarity(compact, entry.compact));
                if (score > best_score) {
                    second_score = best_score;
                    best_score = score;
                    best_path = entry.path;
                } else if (score > second_score) {
                    second_score = score;
                }
            }
            if (best_score >= 0.55 && (best_score - second_score) >= 0.01) {
                log_line("INFO", "[af1c1onados] resolved subgroup " + group_name + " via catalog tree: " + best_path);
                return "https://raw.githubusercontent.com/af1Series1/Tritolgia/main/" + url_encode(best_path, "/");
            }
        } catch (const std::exception& e) {
            log_line("ERROR", "[af1c1onados] catalog fallback failed: " + std::string(e.what()));
        }
        return std::nullopt;
    }

    struct CatalogEntry {
        std::string path;
        std::string strict;
        std::string compact;
    };

    const std::vector<CatalogEntry>& catalog_entries() {
        if (!catalog_entries_.empty()) return catalog_entries_;
        auto response = http_client_.get("https://api.github.com/repos/af1Series1/Tritolgia/git/trees/main?recursive=1",
                                         {{"User-Agent", plugin_user_agent()}}, 20, true);
        auto tree = Json::parse(response.body)["tree"].as_array();
        for (const auto& item : tree) {
            if (item["type"].as_string() != "blob") continue;
            auto path = item["path"].as_string();
            if (path.empty() || path == "AcEStREAM iDs.w3u") continue;
            catalog_entries_.push_back(CatalogEntry{
                path,
                normalize_catalog_name(path, false),
                normalize_catalog_name(path, true)
            });
        }
        return catalog_entries_;
    }

    void collect_groups(const Json& data, const std::string& fallback_group, PlaylistGenerator& playlist,
                        std::map<std::string, std::string>& channels,
                        std::map<std::string, std::string>& picons,
                        std::set<std::string> visited) {
        auto group_name = data["name"].as_string(fallback_group);
        for (const auto& station : data["stations"].as_array()) {
            auto name = station["name"].as_string();
            auto url = station["url"].as_string();
            if (name.empty() || url.empty()) continue;
            auto unique = name;
            int n = 2;
            while (channels.contains(unique)) unique = name + " (" + std::to_string(n++) + ")";
            PlaylistItem item{unique, url_encode(unique, ""), group_name, unique, "", station["image"].as_string()};
            channels[unique] = url;
            picons[unique] = item.logo;
            playlist.add_item(item);
        }
        for (const auto& group : data["groups"].as_array()) {
            auto child_name = group["name"].as_string(group_name);
            if (!group["stations"].as_array().empty()) {
                Json child(Json::object{{"name", child_name}, {"stations", group["stations"]}});
                collect_groups(child, child_name, playlist, channels, picons, visited);
            } else {
                auto url = group["url"].as_string();
                if (url.empty()) continue;
                auto normalized = normalize_github_blob_url(url);
                if (visited.contains(normalized)) continue;

                if (is_shortener_url(normalized)) {
                    if (auto guessed = guess_catalog_url(child_name)) {
                        auto guessed_normalized = normalize_github_blob_url(*guessed);
                        if (!visited.contains(guessed_normalized)) {
                            visited.insert(guessed_normalized);
                            try {
                                auto child = fetch_playlist_json(*guessed);
                                collect_groups(child, child_name, playlist, channels, picons, visited);
                                continue;
                            } catch (const std::exception& fallback_error) {
                                log_line("ERROR", "[af1c1onados] catalog subgroup failed " + child_name + ": " + fallback_error.what());
                            }
                        }
                    }
                }

                visited.insert(normalized);
                try {
                    auto child = fetch_playlist_json(url);
                    collect_groups(child, child_name, playlist, channels, picons, visited);
                } catch (const std::exception& e) {
                    if (auto guessed = guess_catalog_url(child_name)) {
                        try {
                            auto child = fetch_playlist_json(*guessed);
                            collect_groups(child, child_name, playlist, channels, picons, visited);
                            continue;
                        } catch (const std::exception& fallback_error) {
                            log_line("ERROR", "[af1c1onados] fallback subgroup failed " + child_name + ": " + fallback_error.what());
                        }
                    }
                    log_line("ERROR", "[af1c1onados] subgroup failed " + child_name + ": " + e.what());
                }
            }
        }
    }

    std::vector<CatalogEntry> catalog_entries_;
};

class AioPlugin : public Plugin {
public:
    AioPlugin(Config cfg, Proxy& proxy) : config_(std::move(cfg)), proxy_(proxy) {}
    std::string name() const override { return "aio"; }
    std::vector<std::string> handlers() const override { return {"aio"}; }
    bool handle(RequestContext& ctx) override {
        PlaylistGenerator generator(PlaylistGenerator::epg_header(kEpgUrl, 0, true));
        std::set<Plugin*> processed;
        auto handlers = proxy_.plugins().handlers();
        for (const auto& [handler, plugin] : handlers) {
            if (handler == "aio" || handler == "stat" || handler == "statplugin" || handler == "torrenttv_api") continue;
            if (!config_.aio_includes(handler)) continue;
            if (!processed.insert(plugin.get()).second) continue;
            for (auto item : plugin->playlist_items()) {
                auto channels = plugin->channels();
                if (channels.contains(item.name)) item.url = channels[item.name];
                if (item.group.empty()) item.group = handler;
                generator.add_item(item);
            }
        }
        auto body = generator.export_m3u(host_header(ctx), "", ctx.query, false);
        send_bytes(ctx.connection, 200, "audio/mpegurl; charset=utf-8", body);
        return true;
    }
private:
    Config config_;
    Proxy& proxy_;
};

class StatPlugin : public Plugin {
public:
    StatPlugin(Config cfg, Proxy& proxy) : config_(std::move(cfg)), proxy_(proxy) {}
    std::string name() const override { return "stat"; }
    std::vector<std::string> handlers() const override { return {"stat"}; }
    bool handle(RequestContext& ctx) override {
        if (query_get(ctx.query, "action") == "get_status") {
            send_bytes(ctx.connection, 200, "application/json; charset=utf-8", proxy_.status_json().dump());
            return true;
        }
        std::string relative = "index.html";
        if (ctx.path != "/stat") {
            relative = ctx.path.substr(std::string("/stat/").size());
        }
        if (!path_is_safe_relative(relative)) {
            send_bytes(ctx.connection, 404, "text/plain", "Not Found");
            return true;
        }
        try {
            auto full = std::filesystem::path(config_.root_dir) / "http" / relative;
            auto body = read_file_binary(full.string());
            send_bytes(ctx.connection, 200, mime_type_for_path(relative), body);
        } catch (...) {
            send_bytes(ctx.connection, 404, "text/plain", "Not Found");
        }
        return true;
    }
private:
    Config config_;
    Proxy& proxy_;
};

class StatpluginPlugin : public Plugin {
public:
    StatpluginPlugin(Config cfg, Proxy& proxy) : config_(std::move(cfg)), proxy_(proxy) {}
    std::string name() const override { return "statplugin"; }
    std::vector<std::string> handlers() const override { return {"statplugin"}; }
    bool handle(RequestContext& ctx) override {
        auto action = query_get(ctx.query, "action");
        if (action == "get_plugins") {
            send_bytes(ctx.connection, 200, "application/json; charset=utf-8", proxy_.plugins_json().dump(2));
        } else if (action == "check_channel") {
            auto data = proxy_.check_channel_light(query_get(ctx.query, "plugin"), query_get(ctx.query, "channel"), query_get(ctx.query, "content_id"));
            send_bytes(ctx.connection, 200, "application/json; charset=utf-8", data.dump(2));
        } else if (action == "check_peers") {
            int max_wait = 15;
            try { max_wait = std::stoi(query_get(ctx.query, "max_wait", "15")); } catch (...) {}
            max_wait = std::min(30, std::max(5, max_wait));
            auto data = proxy_.check_channel_peers(query_get(ctx.query, "content_id"), max_wait);
            send_bytes(ctx.connection, 200, "application/json; charset=utf-8", data.dump(2));
        } else {
            try {
                auto full = std::filesystem::path(config_.root_dir) / "http" / "statplugin" / "index.html";
                send_bytes(ctx.connection, 200, "text/html; charset=utf-8", read_file_binary(full.string()));
            } catch (...) {
                send_bytes(ctx.connection, 500, "text/plain", "Internal Server Error");
            }
        }
        return true;
    }
private:
    Config config_;
    Proxy& proxy_;
};

std::vector<std::shared_ptr<Plugin>> create_plugins(Config config, HttpClient& http_client, Proxy& proxy) {
    std::vector<std::shared_ptr<Plugin>> plugins;
    auto add = [&](const std::string& name, const std::function<std::shared_ptr<Plugin>()>& factory) {
        if (config.plugin_enabled(name)) {
            auto plugin = factory();
            plugins.push_back(std::move(plugin));
            log_line("INFO", "enabled plugin: " + name);
        }
    };
    add("newera", [&] { return std::make_shared<NewEraPlugin>(config, http_client); });
    add("elcano", [&] { return std::make_shared<ElcanoPlugin>(config, http_client); });
    add("acepl", [&] { return std::make_shared<AcePLPlugin>(config, http_client); });
    add("af1c1onados", [&] { return std::make_shared<Af1c1onadosPlugin>(config, http_client); });
    add("aio", [&] { return std::make_shared<AioPlugin>(config, proxy); });
    add("stat", [&] { return std::make_shared<StatPlugin>(config, proxy); });
    add("statplugin", [&] { return std::make_shared<StatpluginPlugin>(config, proxy); });

    for (auto& plugin : plugins) {
        if (auto playlist = std::dynamic_pointer_cast<PlaylistPlugin>(plugin)) {
            playlist->refresh_if_needed();
        }
    }
    return plugins;
}

} // namespace httpace
