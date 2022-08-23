for angle in `seq 0 4 182`;
do
    echo $angle "agem";
    for shift in 1 2 3 4 5 6;
    do
        echo 'Doing shift ' $shift;
        python3 -m main --dataset cifar100 --tasks 2 --epochs-per-task 20 --lr .03 --gamma 1.0 --batch-size 10 --dropout 0.0 --runs 1 --opt 'agem' --mem-size 1 --angle $angle --shift $shift
    done
done
################################
for angle in `seq 0 4 182`;
do
    echo $angle "tag";
    for shift in 1 2 3 4 5 6;
    do
        echo 'Doing shift ' $shift;
        python3 -m main --dataset cifar100 --tasks 2 --epochs-per-task 20 --lr 0.00025 --gamma 1.0 --batch-size 10 --dropout 0.0 --runs 1 --opt 'tag' --b 5 --tag-opt 'rms' --angle $angle --shift $shift
    done
done
###############################
for angle in `seq 0 4 182`;
do
    echo $angle "er";
    for shift in 1 2 3 4 5 6;
    do
        echo 'Doing shift ' $shift;
        python3 -m main --dataset cifar100 --tasks 2 --epochs-per-task 20 --lr 0.03 --gamma 1.0 --batch-size 10 --dropout 0.0 --runs 1 --opt 'er' --mem-size 1 --angle $angle --shift $shift
    done
done
###########################
#sudo shutdown now