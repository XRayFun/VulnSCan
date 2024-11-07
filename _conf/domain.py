import os

from _conf.base import SCAN_DIR


BRUTEFORCE_OUTPUT_FOLDER = f"{SCAN_DIR}domain/"
if not os.path.exists(BRUTEFORCE_OUTPUT_FOLDER):
    os.mkdir(BRUTEFORCE_OUTPUT_FOLDER)

BRUTEFORCE_OUTPUT_FORMAT = "domain-ip"

BRUTEFORCE_LEVEL = 0

BRUTEFORCE_FILE = None

COMMON_SUBDOMAINS = [
    # Common subdomains
    "www", "mail", "ftp", "api", "blog", "dev", "test", "stage", "webmail", "remote", "ns1", "ns2",
    "smtp", "secure", "server", "vpn", "mx", "docs", "portal", "web", "cpanel", "panel", "support",
    "help", "info", "status", "shop", "billing", "email", "images", "media", "cdn", "static", "m",
    "img", "files", "download", "f", "forum", "client", "admin", "office", "intranet", "partners",
    "gateway", "upload", "cloud", "resources", "public", "private", "internal", "external", "alpha",
    "beta", "prod", "staging", "database", "backup", "btx",

    # Regional and linguistic variations
    "us", "uk", "eu", "cn", "jp", "fr", "de", "es", "it", "br", "ru", "in", "au", "ca", "kr",
    "sa", "ae", "za", "mx", "pl", "se", "ch", "no", "nl", "pt", "id", "tr", "ir", "th", "ar",
    "vn", "ua", "il", "my", "ph", "sg", "bd", "cl", "hk",

    # Contingency and additional options
    "backup1", "backup2", "backup3", "legacy", "old", "archive", "backup-server", "test-server",
    "staging-server", "beta-server", "prod-server", "sandbox", "demo", "test1", "test2", "qa",
    "uat", "stg", "preprod", "prod1", "prod2", "prod3", "legacy1", "legacy2", "old1", "old2",

    # Corporate and team options
    "corp", "enterprise", "sales", "marketing", "engineering", "hr", "finance", "legal", "it",
    "operations", "support", "customer", "helpdesk", "servicedesk", "services", "sup", "cust",
    "hr-portal", "sales-portal", "admin-portal", "team", "team1", "team2", "team3", "team-dev",
    "team-stage", "team-prod", "research", "data", "analytics", "ml", "ai", "devops", "automation",

    # Variants of subdomains with prefixes
    "mobile", "iphone", "android", "tablet", "desktop", "beta-version", "early-access", "securelogin",
    "securemail", "securedoc", "secureportal", "securefile", "securevpn", "ssl", "https", "auth",
    "auth1", "auth2", "auth3", "auth-server", "single-sign-on", "federated", "oauth", "api-gateway",
    "graphql", "json-api", "xml-api", "rest-api", "db", "db1", "db2", "db3", "report", "reporting",
    "logs", "log1", "log2", "log3", "events", "event1", "event2", "event3", "api-docs", "dev-docs",

    # Options for services and applications
    "webapp", "app", "application", "services", "service1", "service2", "service3", "svc", "svc1",
    "svc2", "svc3", "node", "node1", "node2", "node3", "microservices", "ms", "ms1", "ms2", "ms3",
    "app-server", "web-server", "proxy", "reverse-proxy", "frontend", "backend", "pwa", "spa", "ssr",
    "csr", "web-client", "mobile-client", "native-app", "hybrid-app", "mobile-app", "ios-app",
    "android-app", "desktop-app",

    # Random popular subdomains
    "static1", "static2", "cdn1", "cdn2", "cdn3", "files1", "files2", "img1", "img2", "img3",
    "media1", "media2", "media3", "assets", "assets1", "assets2", "downloads", "down", "upload1",
    "upload2", "download1", "download2", "uploads", "cache", "proxy1", "proxy2", "ns3", "ns4",
    "mx1", "mx2", "smtp1", "smtp2", "smtp3", "mail1", "mail2", "mail3", "imap", "pop", "pop3",
    "mailserver", "pop-server", "imap-server", "ftp1", "ftp2", "secureftp", "webftp", "sftp",

    # Options for security and monitoring
    "monitor", "monitoring", "uptime", "health", "status1", "status2", "logs1", "logs2", "logs3",
    "alerts", "alert", "alerts1", "alerts2", "alerts3", "threat", "threats", "threat1", "threat2",
    "siem", "edr", "xdr", "vuln", "vulns", "vulnscan", "scan", "scan1", "scan2", "scan3", "audit",
    "audit1", "audit2", "audit3", "compliance", "compliance1", "policy", "policy1", "policy2",
    "policy3", "log-collector", "log-server", "logstash", "elastic", "kibana", "grafana", "dashboard",

    # Alphabetic and numeric variations of popular subdomains
    *[f'node - {i}' for i in range(1, 1001)],  # Numbered subdomains
    *[f'test-{i}' for i in range(1, 501)],  # Test subdomains
    *[f'backup-{i}' for i in range(1, 501)], # Backup subdomains
    *[f'service-{i}' for i in range(1, 501)],  # Subdomains for services
    *[f'cdn-{i}' for i in range(1, 501)],  # Subdomains for CDNs
    *[f'api-{i}' for i in range(1, 501)],  # Subdomains for APIs
]