echo "Setting up Paper Portraits."
if [ "$EUID" -ne 0 ]
  then echo "Please run as root."
  exit
fi

cat "Installing PIP3..."
