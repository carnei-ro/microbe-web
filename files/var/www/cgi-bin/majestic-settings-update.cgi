#!/usr/bin/haserl
<%in _common.cgi %>
<%
mj_conf=/etc/majestic.yaml
orig_yaml=/tmp/majestic.yaml.original
temp_yaml=/tmp/majestic.yaml

cp -f $mj_conf $temp_yaml

IFS=$'\n' # make newlines the only separator
for name in $(printenv|grep POST_); do
  key=".$(echo $name | sed 's/^POST_mj_//' | cut -d= -f1 | sed 's/_/./g')"
  value="$(echo $name | cut -d= -f2)"

  # validation and normalization
  [ "$key" = ".go.to" ] && goto="$value" && continue
  [ "$key" = ".track" ] && continue
  [ "$key" = ".reset" ] && continue
  [ "$key" = ".netip.password.plain" ] && continue
  if [ "$key" = ".image.rotate" ]; then
    value="${value//°/}"
    [ "$value" = "0" ] && value="none"
  fi

  oldvalue=$(yaml-cli -g "$key" -i $temp_yaml)
  if [ -z "$value" ]; then
    [ -n "$oldvalue" ] && yaml-cli -d $key -i "$temp_yaml" -o "$temp_yaml"
  else
    [ "$oldvalue" != "$value" ] && yaml-cli -s $key "$value" -i "$temp_yaml" -o "$temp_yaml"
  fi
done

[ -n "$(diff -q $temp_yaml $mj_conf)" ] && cp -f $temp_yaml $mj_conf

rm $temp_yaml

if [ -z "$DEBUG" ]; then
  killall -1 majestic
  if [ -n "$goto" ]; then
    redirect_to "$goto"
  else
    redirect_to "/cgi-bin/majestic-config-compare.cgi"
  fi
else
  diff $orig_yaml $mj_conf
  rm $orig_yaml
fi
%>
