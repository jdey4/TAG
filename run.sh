#python3 -m main --dataset 5data --tasks 5 --epochs-per-task 1 --hyp-gs 'lr' --gamma 1.0 --batch-size 64 --dropout 0.0 --runs 1 --opt 'agem' --mem-size 1
#python3 -m main --dataset 5data --tasks 5 --epochs-per-task 1 --hyp-gs 'lr' --gamma 1.0 --batch-size 64 --dropout 0.0 --runs 1 --opt 'er' --mem-size 1
#python3 -m main --dataset 5data --tasks 5 --epochs-per-task 1 --hyp-gs 'tag'  --gamma 1.0 --batch-size 64 --dropout 0.0 --runs 1 --opt 'tag' --b 5 --tag-opt 'rms'

#python3 -m main --dataset 5data --tasks 5 --epochs-per-task 1 --hyp-gs 'lr' --gamma 1.0 --batch-size 64 --dropout 0.0 --runs 1 --opt 'agem' --mem-size 1 --single_task 1
#python3 -m main --dataset 5data --tasks 5 --epochs-per-task 1 --hyp-gs 'lr' --gamma 1.0 --batch-size 64 --dropout 0.0 --runs 1 --opt 'er' --mem-size 1 --single_task 1
#python3 -m main --dataset 5data --tasks 5 --epochs-per-task 1 --hyp-gs 'tag' --gamma 1.0 --batch-size 64 --dropout 0.0 --runs 1 --opt 'tag' --b 5 --tag-opt 'rms' --single_task 1

python3 -m main --dataset cub --tasks 20 --epochs-per-task 1 --lr 0.003 --gamma 1.0 --batch-size 10 --dropout 0.0 --runs 1 --opt 'agem' --mem-size 1