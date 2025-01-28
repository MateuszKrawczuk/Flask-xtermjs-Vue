# Ustawienia podstawowe
bind = "0.0.0.0:5000"  # Adres gniazda, do którego aplikacja ma się podłączyć. Może to być IP:PORT lub gniazdo Unix.
workers = 1              # Liczba procesów roboczych obsługujących żądania.
worker_class = "gthread"    # Typ klas pracowników do użycia. Domyślnie "sync".
threads = 64              # Liczba wątków na proces roboczy. Używane tylko z klasą "gthread".
timeout = 30             # Procesy robocze, które milczą przez więcej niż tę liczbę sekund, są zabijane i restartowane.
graceful_timeout = 10    # Limit czasu na płynne restartowanie procesów roboczych.
keepalive = 2            # Liczba sekund oczekiwania na żądania w połączeniu Keep-Alive.

# Logging
accesslog = "-"          # Plik, do którego zapisywane są logi dostępu. "-" oznacza stdout.
errorlog = "-"           # Plik, do którego zapisywane są logi błędów. "-" oznacza stderr.
loglevel = "info"        # Szczegółowość logów. Opcje: debug, info, warning, error, critical.
capture_output = False    # Przekierowanie stdout/stderr do określonego pliku w `errorlog`.
logger_class = "gunicorn.glogging.Logger"  # Logger używany do rejestrowania zdarzeń w Gunicorn.

# Bezpieczeństwo
limit_request_line = 4094  # Maksymalny rozmiar linii żądania HTTP w bajtach.
limit_request_fields = 100  # Limit liczby nagłówków HTTP w jednym żądaniu.
limit_request_field_size = 8190  # Limit wielkości pojedynczego nagłówka HTTP w bajtach.

# Wydajność
# max_requests = 1000      # Maksymalna liczba żądań obsługiwanych przez proces roboczy przed restartem.
# max_requests_jitter = 50 # Maksymalna losowość dodawana do ustawienia `max_requests`.
# worker_connections = 1000  # Maksymalna liczba jednoczesnych klientów na proces roboczy.

# Debugowanie
reload = False           # Restartowanie procesów roboczych przy zmianie kodu. Użyteczne w środowisku deweloperskim.
reload_engine = "auto"   # Silnik do restartu. Opcje: "auto", "poll", "inotify".
spew = False             # Instalowanie funkcji śledzenia, która wyświetla każdą linijkę wykonaną przez serwer.

# Server Hooks
# on_starting = "myapp:on_starting"  # Wywoływane tuż przed inicjalizacją głównego procesu.
# on_reload = "myapp:on_reload"      # Wywoływane podczas recyklingu procesów roboczych po SIGHUP.
# when_ready = "myapp:when_ready"    # Wywoływane zaraz po uruchomieniu serwera.
# pre_fork = "myapp:pre_fork"        # Wywoływane tuż przed forkiem procesu roboczego.
# post_fork = "myapp:post_fork"      # Wywoływane zaraz po forku procesu roboczego.
# post_worker_init = "myapp:post_worker_init"  # Wywoływane po zainicjowaniu aplikacji przez proces roboczy.
# worker_int = "myapp:worker_int"    # Wywoływane, gdy proces roboczy odbiera sygnał SIGINT lub SIGQUIT.
# worker_abort = "myapp:worker_abort"  # Wywoływane, gdy proces roboczy odbiera sygnał SIGABRT.
# pre_exec = "myapp:pre_exec"        # Wywoływane tuż przed forkiem nowego głównego procesu.
# pre_request = "myapp:pre_request"  # Wywoływane tuż przed obsłużeniem żądania przez proces roboczy.
# post_request = "myapp:post_request"  # Wywoływane zaraz po obsłużeniu żądania przez proces roboczy.
# child_exit = "myapp:child_exit"    # Wywoływane zaraz po zakończeniu procesu roboczego.
# worker_exit = "myapp:worker_exit"  # Wywoływane zaraz po zakończeniu procesu roboczego.
# nworkers_changed = "myapp:nworkers_changed"  # Wywoływane, gdy zmienia się liczba procesów roboczych.

# SSL
# keyfile = "/path/to/your/keyfile.key"  # Plik klucza SSL.
# certfile = "/path/to/your/certfile.crt"  # Plik certyfikatu SSL.
# ca_certs = "/path/to/your/ca_certs.crt"  # Plik certyfikatów CA.
# ssl_version = "TLSv1_2"  # Wersja SSL do użycia (TLSv1, TLSv1_1, TLSv1_2, itp.).
# ciphers = "HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA"  # Algorytmy szyfrowania SSL do użycia.

# Różne
# chdir = "/path/to/your/app"  # Zmiana katalogu roboczego przed załadowaniem aplikacji.
# user = "www-data"          # Uruchamianie procesów roboczych jako określony użytkownik.
# group = "www-data"         # Uruchamianie procesów roboczych jako określona grupa.
# umask = 0                  # Maska bitowa dla trybu plików tworzonych przez Gunicorn.
# proc_name = "myapp"        # Podstawowa nazwa do ustawienia w procesach roboczych.
# sendfile = True            # Czy używać wywołania systemowego `sendfile` do kopiowania danych między deskryptorami plików.
# reuse_port = False         # Ustawienie flagi SO_REUSEPORT na gnieździe nasłuchującym.