import torchvision
import torchvision.transforms.functional as TorchVisionFunc
from get_cub import *
from get_datasets import *
from tqdm import tqdm

def get_permuted_mnist(task_id, batch_size):
	"""
	Get the dataset loaders (train and test) for a `single` task of permuted MNIST.
	This function will be called several times for each task.
	
	:param task_id: id of the task [starts from 1]
	:param batch_size:
	:return: a tuple: (train loader, test loader)
	"""
	
	# convention, the first task will be the original MNIST images, and hence no permutation
	if task_id == 1:
		idx_permute = np.array(range(784))
	else:
		idx_permute = torch.from_numpy(np.random.RandomState().permutation(784))
	transforms = torchvision.transforms.Compose([torchvision.transforms.ToTensor(),
				torchvision.transforms.Lambda(lambda x: x.view(-1)[idx_permute] ),
				])
	mnist_train = torchvision.datasets.MNIST('./data/', train=True, download=True, transform=transforms)
	train_loader = torch.utils.data.DataLoader(mnist_train, batch_size=batch_size, num_workers=4, pin_memory=True, shuffle=True)
	test_loader = torch.utils.data.DataLoader(torchvision.datasets.MNIST('./data/', train=False, download=True, transform=transforms),  batch_size=256, shuffle=False, num_workers=4, pin_memory=True)

	return train_loader, test_loader


def get_permuted_mnist_tasks(num_tasks, batch_size):
	"""
	Returns the datasets for sequential tasks of permuted MNIST
	
	:param num_tasks: number of tasks.
	:param batch_size: batch-size for loaders.
	:return: a dictionary where each key is a dictionary itself with train, and test loaders.
	"""
	datasets = {}
	for task_id in range(1, num_tasks+1):
		train_loader, test_loader = get_permuted_mnist(task_id, batch_size)
		datasets[task_id] = {'train': train_loader, 'test': test_loader}
	return datasets


class RotationTransform:
	"""
	Rotation transforms for the images in `Rotation MNIST` dataset.
	"""
	def __init__(self, angle):
		self.angle = angle

	def __call__(self, x):
		return TorchVisionFunc.rotate(x, self.angle, fill=(0,))


def get_rotated_mnist(task_id, batch_size):
	"""
	Returns the dataset for a single task of Rotation MNIST dataset
	:param task_id:
	:param batch_size:
	:return:
	"""
	per_task_rotation = 10
	rotation_degree = (task_id - 1)*per_task_rotation
	rotation_degree -= (np.random.random()*per_task_rotation)

	transforms = torchvision.transforms.Compose([
		RotationTransform(rotation_degree),
		torchvision.transforms.ToTensor(),
		])

	train_loader = torch.utils.data.DataLoader(torchvision.datasets.MNIST('./data/', train=True, download=True, transform=transforms), batch_size=batch_size, shuffle=True, num_workers=4, pin_memory=True)
	test_loader = torch.utils.data.DataLoader(torchvision.datasets.MNIST('./data/', train=False, download=True, transform=transforms),  batch_size=256, shuffle=False, num_workers=4, pin_memory=True)

	return train_loader, test_loader


def get_rotated_mnist_tasks(num_tasks, batch_size):
	"""
	Returns data loaders for all tasks of rotation MNIST dataset.
	:param num_tasks: number of tasks in the benchmark.
	:param batch_size:
	:return:
	"""
	datasets = {}
	for task_id in range(1, num_tasks+1):
		train_loader, test_loader = get_rotated_mnist(task_id, batch_size)
		datasets[task_id] = {'train': train_loader, 'test': test_loader}
	return datasets


def get_split_cifar100(task_id, classes, batch_size, cifar_train, cifar_test):
	"""
	Returns a single task of split CIFAR-100 dataset
	:param task_id:
	:param batch_size:
	:return:
	"""


	start_class = (task_id-1)*classes
	end_class = task_id * classes

	targets_train = torch.tensor(cifar_train.targets)
	target_train_idx = ((targets_train >= start_class) & (targets_train < end_class))
	
	targets_test = torch.tensor(cifar_test.targets)
	target_test_idx = ((targets_test >= start_class) & (targets_test < end_class))
	train_loader = torch.utils.data.DataLoader(torch.utils.data.dataset.Subset(cifar_train, np.where(target_train_idx==1)[0]), batch_size=batch_size, shuffle=True)
	test_loader = torch.utils.data.DataLoader(torch.utils.data.dataset.Subset(cifar_test, np.where(target_test_idx==1)[0]), batch_size=batch_size)

	return train_loader, test_loader


def get_split_cifar100_tasks(num_tasks, batch_size):
	"""
	Returns data loaders for all tasks of split CIFAR-100
	:param num_tasks:
	:param batch_size:
	:return:
	"""
	datasets = {}
	
	# convention: tasks starts from 1 not 0 !
	# task_id = 1 (i.e., first task) => start_class = 0, end_class = 4
	cifar_transforms = torchvision.transforms.Compose([torchvision.transforms.ToTensor(),])
	cifar_train = torchvision.datasets.CIFAR100('./data/', train=True, download=True, transform=cifar_transforms)
	cifar_test = torchvision.datasets.CIFAR100('./data/', train=False, download=True, transform=cifar_transforms)
	classes = int(100/num_tasks)

	for task_id in range(1, num_tasks+1):
		train_loader, test_loader = get_split_cifar100(task_id, classes, batch_size, cifar_train, cifar_test)
		datasets[task_id] = {'train': train_loader, 'test': test_loader}
	return datasets


def get_split_cub(task_id, classes, batch_size, train_X, test_X, train_Y, test_Y):
	"""
	Returns a single task of split CUB dataset
	:param task_id:
	:param batch_size:
	:return:
	"""
	start_class = (task_id - 1) * classes
	end_class = task_id * classes

	target_train_idx = ((train_Y >= start_class) & (train_Y < end_class))
	target_test_idx = ((test_Y >= start_class) & (test_Y < end_class))

	train_loader = torch.utils.data.DataLoader(
		torch.utils.data.dataset.Subset(tuple(zip(train_X,train_Y)), np.where(target_train_idx == 1)[0]), batch_size=batch_size,
		shuffle=True)
	test_loader = torch.utils.data.DataLoader(
		torch.utils.data.dataset.Subset(tuple(zip(test_X,test_Y)), np.where(target_test_idx == 1)[0]), batch_size=batch_size)

	return train_loader, test_loader



def get_split_cub_tasks(num_tasks, batch_size):
	"""
	Returns data loaders for all tasks of split CUB
	:param num_tasks:
	:param batch_size:
	:return:
	"""
	datasets = {}

	cub_train = Cub2011('./data/', train=True, download=True)
	train_X, train_Y, test_X, test_Y = [], [], [], []
	for i in tqdm(range(len(cub_train))):
		x, y = cub_train.__getitem__(i)
		train_X+=[x]
		train_Y+=[y]
	train_X, train_Y = np.array(train_X), np.array(train_Y)
	cub_test = Cub2011('./data/', train=False, download=True)
	for i in tqdm(range(len(cub_test))):
		x, y = cub_train.__getitem__(i)
		test_X+=[x]
		test_Y+=[y]
	test_X, test_Y = np.array(test_X), np.array(test_Y)
	classes = int(200/num_tasks)
	# train_X, train_Y, test_X, test_Y = _CUB_get_data('./data/CUB_200_2011/images', './data/CUB_200_2011/CUB_train_list.txt', './data/CUB_200_2011/CUB_test_list.txt', 224, 224)
	for task_id in range(1, num_tasks + 1):
		train_loader, test_loader = get_split_cub(task_id, classes, batch_size, train_X, test_X, train_Y, test_Y)
		datasets[task_id] = {'train': train_loader, 'test': test_loader}
	return datasets

# if __name__ == "__main__":
# 	dataset = get_split_cifar100(1)



