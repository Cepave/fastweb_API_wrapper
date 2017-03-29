# trouble shooting

for the error `ImportError: no module named request`


in Ubuntu
```
sudo apt-get install request
```


in CentOS

```
yum install python-pip
pip install requests

```

# for yaml dependency

use
```
pip install pyyaml
```

or
```
sudo apt-get install python-yaml  # in Ubuntu
yum install python-yaml           # in CentOS
```


# for arrow dependency
```
pip install arrow
```

# Recommended utility

```
apt-get install jq  # in Ubuntu
yum install jq      # in CentOS
```


# setup 

fill in the `username`, `password` in `secret.yaml`

# typical use

```
./history.py 2017-02-28T06:01:00+0800 2017-03-28T06:01:00+0800 c01.i07 | jq '.'
```
