if [[ $OSTYPE == "linux-gnu"* ]];
then
source ../.env/bin/activate
elif [[ $OSTYPE == "msys"* ]];
then
source ../.env/scripts/activate
else
  echo "Error: Cannot recognize OSTYPE"
fi