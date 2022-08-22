import argparse
import matplotlib

matplotlib.use('Agg')
from models import *
from data.data_utils import *

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'


def apply_mask(mem_y, out, n_classes):
	"""
	Apply mask on the predicted outputs based on the given task - assuming task-incremental learning setup
	:param mem_y: Actual labels
	:param out: Predictions
	:param n_classes: Number of classes per task
	:return: Masked predictions
	"""
	for i,y in enumerate(mem_y):
		mask = torch.zeros_like(out[i])
		mask[y-(y%n_classes):y-(y%n_classes)+n_classes]=1
		out[i] = out[i].masked_fill(mask == 0, -1e10)
	return out


def parse_arguments():
	"""
	Parse and print the relevant arguments
	"""
	parser = argparse.ArgumentParser(description='Argument parser')
	parser.add_argument('--tasks', default=5, type=int, help='total number of tasks')
	parser.add_argument('--epochs-per-task', default=1, type=int, help='epochs per task')
	parser.add_argument('--dataset', default='rot-mnist', type=str, help='dataset. options: rot-mnist, perm-mnist, cifar100')
	parser.add_argument('--batch-size', default=10, type=int, help='batch-size')
	parser.add_argument('--opt', default='', type=str, help='Manual adagrad')
	parser.add_argument('--lr', default=0.1, type=float, help='learning rate')
	parser.add_argument('--gamma', default=0.4, type=float, help='learning rate decay. Use 1.0 for no decay')
	parser.add_argument('--dropout', default=0.25, type=float, help='dropout probability. Use 0.0 for no dropout')
	parser.add_argument('--hiddens', default=256, type=int, help='num of hidden neurons in each layer of a 2-layer MLP')
	parser.add_argument('--compute-eigenspectrum', default=False, type=bool, help='compute eigenvalues/eigenvectors?')
	parser.add_argument('--b', default=None, type=int, help='b')
	parser.add_argument('--seed', default=0, type=int, help='random seed')
	parser.add_argument('--runs', default=3, type=int, help='# runs')
	parser.add_argument('--hyp-gs', default='', type=str, help='Hyperparameter search')
	parser.add_argument('--tag-opt', default='adam', type=str, help='tag opt')
	parser.add_argument('--mem-size', default=1, type=int, help='mem')
	parser.add_argument('--multi', default=0, type=int, help='MTL')
	parser.add_argument('--lambd', default=1, type=int, help='EWC')
	parser.add_argument('--slot', default=0, type=int, help='slot')
	parser.add_argument('--shift', default=1, type=int, help='shift')
	parser.add_argument('--run_500', default=True, type=int, help='run 500 samples?')

	args = parser.parse_args()
	print("Parameters:\n  benchmark="+str(args.dataset)+"\n  num_tasks="+str(args.tasks)+"\n  "+
		  "runs="+str(args.runs)+"\n  epochs-per-task="+str(args.epochs_per_task)+
	      "\n  batch_size="+str(args.batch_size)+"\n  "+"learning_rate="+str(args.lr)+"\n  learning rate decay(gamma)="
	      +str(args.gamma)+"\n  dropout prob="+str(args.dropout)+ "\n  optimizer opt="
	      +(str(args.opt) if args.opt!='' else 'sgd'))
	if args.opt=='':
		return args
	if 'er' in args.opt or 'agem' in args.opt:
		print("  mem="+str(args.mem_size))
	if 'tag' in args.opt:
		print("  tag-opt="+str(args.tag_opt))
		print("  b="+str(args.b))
	if 'ewc' in args.opt:
		print("  lambda="+str(args.lambd))
	return args


def set_seeds(seed):
	"""
	Set seeds for reproducibility
	"""
	os.environ['PYTHONHASHSEED'] = str(seed)
	np.random.seed(seed)
	torch.manual_seed(seed)
	torch.cuda.manual_seed(seed)
	torch.cuda.manual_seed_all(seed)
	torch.backends.cudnn.benchmark = False
	torch.backends.cudnn.deterministic = True


def init_experiment(args):
	"""
	Initialize the experiment and logging dictionaries
	"""
	print('\n------------------- Experiment-'+str(args.seed)+' started -----------------')
	set_seeds(args.seed)
	loss_db = {t: [0 for i in range(args.tasks)] for t in range(1, args.tasks+1)}
	acc_db = {t: [0 for i in range(args.tasks)] for t in range(1, args.tasks+1)}
	return acc_db, loss_db


def end_experiment(args, acc_db, loss_db):
	"""
	Print the final metrics
	"""
	score = np.mean([acc_db[i][-1] for i in acc_db.keys()])
	forget = np.mean([max(acc_db[i])-acc_db[i][-1] for i in range(1, args.tasks)])/100.0
	la = np.mean([acc_db[i][i-1] for i in acc_db.keys()])
	print('average accuracy = {}, forget = {}, learning accuracy = {}'.format(score, forget, la))
	return score, forget, la


def get_benchmark_model(args):
	"""
    Return the corresponding PyTorch model for experiment
    """
	if 'mnist' in args.dataset:
		if args.tasks == 20 and args.hiddens < 256:
			print("Warning! the main paper MLP with 256 neurons for experiment with 20 tasks")
		return MLP(args.hiddens, {'dropout': args.dropout, 'total_classes': args.tasks*10, 'classes': 10}).to(DEVICE)
	elif 'cifar' in args.dataset:
		if args.tasks==10:
			#return AlexNet(config={'input_size': (3, 32, 32), 'total_classes': 100, 'classes': int(100 / args.tasks)}).to(DEVICE)
			return gido(config={'input_size': (3, 32, 32), 'total_classes': 100, 'classes': int(100 / args.tasks)}).to(DEVICE)
		return ResNet18(config={'input_size': (3, 32, 32), 'dropout': args.dropout, 'classes': int(100 / args.tasks)}).to(DEVICE)
	elif 'mini_imagenet' in args.dataset:
		return ResNet18(config={'input_size': (3, 84, 84), 'dropout': args.dropout, 'classes': int(100 / args.tasks)}).to(DEVICE)
	elif 'cub' in args.dataset:
		return ResNet18_CUB(config={'input_size': (3, 224, 224), 'dropout': args.dropout, 'classes': int(200 / args.tasks)}).to(DEVICE)
	elif '5data' in args.dataset:
		return ResNet18(config={'input_size': (3, 32, 32), 'dropout': args.dropout, 'classes': int(50 / args.tasks)}).to(DEVICE)
	else:
		raise Exception("Unknown dataset.\n" + "The code supports 'perm-mnist, rot-mnist, and cifar-100.")


def log_metrics(metrics, time, task_id, acc_db, loss_db, p=False):
	"""
	Log accuracy and loss at different times of training
	"""
	if p:
		print('epoch {}, task:{}, metrics: {}'.format(time, task_id, metrics))
	# log to db
	acc = metrics['accuracy']
	loss = metrics['loss']
	loss_db[task_id][time-1] = loss
	acc_db[task_id][time-1] = acc
	return acc_db, loss_db


def print_details(tag, prev_task_id, metrics, alpha):
	"""
	Print test accuracy on past task datasets (along with )
	"""
	if tag:
		print('\tPrev Task:', prev_task_id, ' \tManual\t', metrics['accuracy'], '   \t', alpha[prev_task_id - 1])
	else:
		print('\tPrev Task:', prev_task_id, ' \tManual\t', metrics['accuracy'])


def hyp_lr(args, avg_runs_exp):
	"""
	Grid search over Learning rate
	"""
	lrs = (0.1, 0.05, 0.01, 0.001)
	best_hyp, best_acc = 0, 0
	for lr in lrs:
		args.lr = lr
		print(args.lr)
		args.seed = 0
		acc = avg_runs_exp(args.runs, validate=True)
		if acc > best_acc:
			best_acc = acc
			best_hyp = lr
	print('Best [lr]:', best_hyp)


def hyp_tag(args, avg_runs_exp):
	"""
	Grid search for TAG: Learning rate and b
	"""
	bs = (5,1,7, 3)
	lrs = (0.005, 0.001, 0.0005, 0.0001, 0.00005, 0.00001)
	best_hyp, best_acc = 0, 0
	for b in bs:
		args.b = b
		for lr in lrs:
			args.lr = lr
			print(args.lr, args.b)
			args.seed = 0
			acc = avg_runs_exp(args.runs, validate=True)
			if acc > best_acc:
				best_acc = acc
				best_hyp = [lr,b]
	print('Best [lr, b]:', best_hyp)


def hyp_ewc(args, avg_runs_exp):
	"""
	Grid search for EWC: Learning rate and Lambda
	"""
	ls, lambdas = (0.1, 0.05, 0.01, 0.001), (1, 10, 100)
	best_hyp, best_acc = 0, 0
	for l in ls:
		args.lr =l
		for b in lambdas:
			args.lambd = b
			print(l, b)
			args.seed = 0
			acc = avg_runs_exp(args.runs, validate=True)
			if acc > best_acc:
				best_acc = acc
				best_hyp = [l,b]
	print('Best [lr, lambda]:', best_hyp)


def hyp_stable(args, avg_runs_exp):
	"""
	Grid search for Stable SGD: Learning rate, decay and Dropout
	"""
	dropouts = (0.0, 0.1, 0.25, 0.5)
	lrs = (0.1, 0.05, 0.01)
	decays = (0.9, 0.8, 0.7)
	best_hyp, best_acc = 0, 0
	for dropout in dropouts:
		args.dropout = dropout
		for lr in lrs:
			args.lr = lr
			for b in decays:
				args.gamma = b
				print(dropout, lr, b)
				args.seed = 0
				acc = avg_runs_exp(args.runs, validate=True)
				if acc>best_acc:
					best_acc = acc
					best_hyp = [dropout, lr, b]
	print('Best [dropout, lr, decay]:', best_hyp)

