
set -e errexit
set -e pipefail
set -e nounsetcle
set -e xtrace

C='\e[0;36m'     # cyan
Y='\033[0;33m'   # yellow
G='\033[0;32m'   # green 
B='\033[0;34m'   # blue
W='\033[0;37m'   # white
E='\033[0m'      # end



DB_HOST="$POSTGRES_HOST"
DB_USERNAME="$POSTGRES_USER"
DB_PASSWORD="$POSTGRES_PASSWORD"

# Exporting all environment variables to use in crontab
env | sed 's/^\(.*\)$/ \1/g' > /root/env

echo "${C}____________________________________________________________________________________________________________________________${E}"
echo "${C}=> WAIT POSTGRES DB TO BE READY"
sleep 5
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USERNAME" -c '\q'; do
  >&2 echo "${Y}Postgres is unavailable - sleeping..."
  sleep 2
done
echo "${G}Postgres is ready!"

echo "${C}____________________________________________________________________________________________________________________________${E}"
echo "${C}=> MAKING MIGRATIONS                                                                                                        ${E}"
python manage.py makemigrations

echo "${C}____________________________________________________________________________________________________________________________${E}"
echo "${C}=> RUNNING MIGRATIONS                                                                                                       ${E}"
python manage.py migrate 

echo "${C}____________________________________________________________________________________________________________________________${E}"
echo "${C}=> STARTING CRON${E}"
echo 'Cronjobs sige-cron in operating system'
/bin/cp /sige-slave/crons/cronjob /etc/cron.d/sige-cron
crontab /etc/cron.d/sige-cron
cron

cronitor list /etc/cron.d/sige-cron

echo "${C}____________________________________________________________________________________________________________________________${E}"
echo "${C}=> RUNNING SERVER                                                                                                           ${E}"
echo '\e[1;33m                                                              ۞         ___ _  __ _  ___     ___ _     __  __   __ __      '
echo '\e[1;33m                                                            ۞   ۞      / __| |/ _` |/ _ \   / __| |   / _` \ \ / / _ \    '
echo '\e[1;33m                                                          ۞   ۞   ۞    \__ \ | (_| | ___/   \__ \ |__| (_| |\ V / ___/    '
echo '\e[1;33m                                                            ۞   ۞      |___/_|\__, |\___|   |___/____/\__,_| \_/ \___|    '
echo '\e[1;33m                                                              ۞               |___/                                        '
echo "Starting ${W}"${API_NAME}"${E} - ${G}http://"${API_HOST}":${API_PORT}${E}                                               ${B}UnB ${Y}Energia   "
echo "         ${W}${DB_HOST}${E}  - ${Y}http://"${API_HOST}":${POSTGRES_PORT}${E}                                                        ${B}Eficiencia Energetica"
echo "${C}____________________________________________________________________________________________________________________________${E}"
python manage.py runserver ${API_HOST}:${API_PORT}

                    
#   ∩ │◥███◣ ╱◥███◣   
#   ╱◥◣ ◥████◣▓∩▓│∩ ║ 
#   │╱◥█◣║∩∩∩ ║◥█▓ ▓█◣
#    ││∩│ ▓ ║∩田│║▓ ▓ ▓


# Obtenha o endereço IP da máquina 'Slave'
# IP=$(hostname -I | awk '{print $1}')
# Registre o serviço no Consul
# curl --request PUT --data '{\'Name\': \'slave-service\', \'Address\': \'$IP\', \'Port\': 8000}' http://consul-host:8500/v1/agent/service/register
# Inicie o servidor
# python manage.py runserver 0.0.0.0:8000 --verbosity 3
