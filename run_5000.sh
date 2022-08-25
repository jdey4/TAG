for shift in $(seq 1 1 7);
do 
    echo 'doing agem ' $shift 
    CUDA_VISIBLE_DEVICES=2,3 python3 -m main --dataset cifar100 --tasks 10 --epochs-per-task 20 --lr .03 --gamma 1.0 --batch-size 10 --dropout 0.0 --runs 1 --opt 'agem' --mem-size 1 --shift $shift --run_500 0
done

for shift in $(seq 1 1 7);
do 
    echo 'doing tag ' $shift 
    CUDA_VISIBLE_DEVICES=2,3 python3 -m main --dataset cifar100 --tasks 10 --epochs-per-task 20 --lr 0.00025 --gamma 1.0 --batch-size 10 --dropout 0.0 --runs 1 --opt 'tag' --b 5 --tag-opt 'rms' --shift $shift --run_500 0
done

for shift in $(seq 1 1 7);
do 
    echo 'doing er ' $shift 
    CUDA_VISIBLE_DEVICES=2,3 python3 -m main --dataset cifar100 --tasks 10 --epochs-per-task 20 --lr 0.03 --gamma 1.0 --batch-size 10 --dropout 0.0 --runs 1 --opt 'er' --mem-size 1 --shift $shift --run_500 0
done