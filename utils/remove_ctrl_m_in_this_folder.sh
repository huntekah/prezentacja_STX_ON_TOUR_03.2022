for f in *; do cat $f | sed -e "s/^M/ /g" | sponge $f ; done
