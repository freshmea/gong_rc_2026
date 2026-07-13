sudo cp /etc/hostapd/hostapd.conf.org /etc/hostapd/hostapd.conf
hn="s/ssid=/ssid=$(hostname)/g"
echo $hn
sudo sed -i -e $hn /etc/hostapd/hostapd.conf
sudo /sbin/iw dev wlan0 interface add ap0 type __ap
sudo hostapd /etc/hostapd/hostapd.conf
