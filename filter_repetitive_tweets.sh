TWEETS_LOCATION="tweets"
for file in ${TWEETS_LOCATION}/*;
  do
    echo $file;
    cat $file | sort | uniq | sponge $file;
  done