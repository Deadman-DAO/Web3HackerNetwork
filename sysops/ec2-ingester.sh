sudo apt update && sudo apt upgrade -y
sudo apt install -y emacs-nox git python3 pip unzip
sudo pip install duckdb pandas boto3 pyarrow
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
git clone https://github.com/Deadman-DAO/Web3HackerNetwork.git

echo '-----------------------------'
echo 'now run scp -i .ssh/keyfile.pem -r ~/.aws admin@ip:./'
echo '-----------------------------'


# 00: 921164
# 00: 971188
