import numpy as np
import torch
import torch.nn as nn
from torch.nn.functional import relu, avg_pool2d
from torch.nn import functional as F
import torchvision.models as models


def conv3x3(in_planes, out_planes, stride=1):
	return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride, padding=1, bias=False)

class gido(nn.Module):
	def __init__(self, config):
		super(gido, self).__init__()
		self.n_classes = config['classes']
		self.total_classes = config['total_classes']
		self.layer1 = nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1, bias=False)
		self.bn1 = nn.BatchNorm2d(16)
		self.relu1 = nn.ReLU()
		self.layer2 = nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1, bias=False)
		self.bn2 = nn.BatchNorm2d(32)
		self.relu2 = nn.ReLU()
		self.layer3 = nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1, bias=False)
		self.bn3 = nn.BatchNorm2d(64)
		self.relu3 = nn.ReLU()
		self.layer4 = nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1, bias=False)
		self.bn4 = nn.BatchNorm2d(128)
		self.relu4 = nn.ReLU()
		self.layer5 = nn.Conv2d(128, 254, kernel_size=3, stride=2, padding=1, bias=False)
		self.bn5 = nn.BatchNorm2d(254)
		self.relu5 = nn.ReLU()
		self.fc1 = nn.Linear(in_features=254*2*2, out_features=2000)
		self.bn_fc1 = nn.BatchNorm1d(2000)
		self.relu_fc1 = nn.ReLU()
		self.fc2 = nn.Linear(in_features=2000, out_features=2000)
		self.bn_fc2 = nn.BatchNorm1d(2000)
		self.relu_fc2 = nn.ReLU()
		self.fc3 = nn.Linear(in_features=2000, out_features=self.total_classes)

		self.softmax = nn.Softmax()

	def forward(self, x, task_id=None):
		out = self.layer1(x.float())
		out = self.bn1(out)
		out = self.relu1(out)
		out = self.layer2(out)
		out = self.bn2(out)
		out = self.relu2(out)
		out = self.layer3(out)
		out = self.bn3(out)
		out = self.relu3(out)
		out = self.layer4(out)
		out = self.bn4(out)
		out = self.relu4(out)
		out = self.layer5(out)
		out = self.bn5(out)
		out = self.relu5(out)
		#print(out.shape)
		#out = nn.Flatten(out, 1)
		out = out.view(-1, 254 * 2 * 2)
		out = self.fc1(out)
		out = self.bn_fc1(out)
		out = self.relu_fc1(out)
		out = self.fc2(out)
		out = self.bn_fc2(out)
		out = self.relu_fc2(out)
		out = self.fc3(out)

		if task_id is None:
			return out
		offset1 = int((task_id - 1) * self.n_classes)
		offset2 = int(task_id * self.n_classes)
		if offset1 > 0:
			out[:, :offset1].data.fill_(0)
		if offset2 < self.total_classes:
			out[:, offset2:self.total_classes].data.fill_(0)

		out = self.softmax(out)
		return out


class ResNet18_CUB(nn.Module):
	"""
	Resnet18 (pretrained on Imagenet) for CUB benchmark
	"""

	def __init__(self, config):
		super(ResNet18_CUB, self).__init__()
		resnet = models.resnet18(pretrained=True)
		for param in resnet.parameters():
			param.requires_grad = True
		self.net = resnet
		self.net.fc = nn.Linear(resnet.fc.in_features, 200)
		self.input_size = config['input_size']
		self.n_classes = config['classes']

	def forward(self, x, task_id=None):
		x = x.view(x.size(0), *self.input_size)
		out = self.net(x)
		if task_id is None:
			return out
		t = task_id
		offset1 = int((t - 1) * self.n_classes)
		offset2 = int(t * self.n_classes)
		if offset1 > 0:
			out[:, :offset1].data.fill_(-10e10)
		if offset2 < 200:
			out[:, offset2:200].data.fill_(-10e10)
		return out


class MLP(nn.Module):
	"""
	Two layer MLP for MNIST benchmarks.
	Refer: https://github.com/imirzadeh/stable-continual-learning/blob/master/stable_sgd/models.py
	"""
	def __init__(self, hiddens, config):
		super(MLP, self).__init__()
		self.n_classes = config['classes']
		self.total_classes = config['total_classes']
		self.W1 = nn.Linear(784, hiddens)
		self.relu = nn.ReLU(inplace=True)
		self.dropout_1 = nn.Dropout(p=config['dropout'])
		self.W2 = nn.Linear(hiddens, hiddens)
		self.dropout_2 = nn.Dropout(p=config['dropout'])
		self.W3 = nn.Linear(hiddens, self.total_classes)

	def forward(self, x, task_id=None):
		x = x.view(-1, 784)
		out = self.W1(x)
		out = self.relu(out)
		out = self.dropout_1(out)
		out = self.W2(out)
		out = self.relu(out)
		out = self.dropout_2(out)
		out = self.W3(out)
		if task_id is None:
			return out
		offset1 = int((task_id - 1) * self.n_classes)
		offset2 = int(task_id * self.n_classes)
		if offset1 > 0:
			out[:, :offset1].data.fill_(-10e10)
		if offset2 < self.total_classes:
			out[:, offset2:self.total_classes].data.fill_(-10e10)
		return out


class BasicBlock(nn.Module):
	"""
	Basic Block for Reduced ResNet
	Refer: https://github.com/imirzadeh/stable-continual-learning/blob/master/stable_sgd/models.py
	"""
	expansion = 1

	def __init__(self, in_planes, planes, stride=1, config={}):
		super(BasicBlock, self).__init__()
		self.conv1 = conv3x3(in_planes, planes, stride)
		# self.conv2 = conv3x3(planes, planes)

		self.shortcut = nn.Sequential()
		if stride != 1 or in_planes != self.expansion * planes:
			self.shortcut = nn.Sequential(
				nn.Conv2d(in_planes, self.expansion * planes, kernel_size=1,
				          stride=stride, bias=False),
			)

		self.bn1 = nn.Sequential(
			nn.BatchNorm2d(planes),
			nn.Dropout(p=config['dropout'])
		)

		self.bn2 = nn.Sequential(
			nn.BatchNorm2d(planes),
			nn.Dropout(p=config['dropout'])
		)

	def forward(self, x):
		out = self.conv1(x)
		out = relu(out)
		out = self.bn1(out)

		out += self.shortcut(x)
		out = relu(out)
		out = self.bn2(out)
		return out


class ResNet(nn.Module):
	"""
	Reduced ResNet - used in methods like ER and Stable SGD.
	Refer: https://github.com/imirzadeh/stable-continual-learning/blob/master/stable_sgd/models.py
	"""
	def __init__(self, block, num_blocks, num_classes, nf, config={}):
		super(ResNet, self).__init__()
		self.in_planes = nf
		self.input_size = config['input_size']
		self.n_classes = config['classes']
		self.avg_pool = 4 if 'avg_pool' not in config else config['avg_pool']
		self.stride1 = 1 if 'stride1' not in config else config['stride1']
		self.conv1 = conv3x3(self.input_size[0], nf * 1)
		self.bn1 = nn.BatchNorm2d(nf * 1)
		self.layer1 = self._make_layer(block, nf * 1, num_blocks[0], stride=self.stride1, config=config)
		self.layer2 = self._make_layer(block, nf * 2, num_blocks[1], stride=2, config=config)
		self.layer3 = self._make_layer(block, nf * 4, num_blocks[2], stride=2, config=config)
		self.layer4 = self._make_layer(block, nf * 8, num_blocks[3], stride=2, config=config)
		last_hid = nf * 8 * block.expansion if self.input_size[1] in [8, 16, 21, 32, 42] else 640
		if 'avg_pool' in config:
			last_hid = 1440
		self.linear = nn.Linear(last_hid, num_classes)

	def _make_layer(self, block, planes, num_blocks, stride, config):
		strides = [stride] + [1] * (num_blocks - 1)
		layers = []
		for stride in strides:
			layers.append(block(self.in_planes, planes, stride, config=config))
			self.in_planes = planes * block.expansion
		return nn.Sequential(*layers)

	def forward(self, x, task_id=None):
		bsz = x.size(0)
		out = relu(self.bn1(self.conv1(x.view(bsz, *self.input_size))))
		out = self.layer1(out)
		out = self.layer2(out)
		out = self.layer3(out)
		out = self.layer4(out)
		out = avg_pool2d(out, self.avg_pool)
		out = out.view(out.size(0), -1)
		out = self.linear(out)
		if task_id is None:
			return out
		offset1 = int((task_id - 1) * self.n_classes)
		offset2 = int(task_id * self.n_classes)
		if offset1 > 0:
			out[:, :offset1].data.fill_(-10e10)
		if offset2 < 100:
			out[:, offset2:100].data.fill_(-10e10)
		return out


def ResNet18(nclasses=100, nf=20, config={}):
	net = ResNet(BasicBlock, [2, 2, 2, 2], nclasses, nf, config=config)
	return net


class AlexNet(torch.nn.Module):
	"""
	5-layer version of AlexNet for GPM purposes
	Refer: https://github.com/joansj/hat/blob/master/src/networks/alexnet.py
	"""
	def __init__(self, config):
		super(AlexNet, self).__init__()

		ncha, size, _ = config['input_size']
		self.n_classes = config['classes']
		self.total_classes = config['total_classes']
		self.conv1 = torch.nn.Conv2d(ncha, 64, kernel_size=size // 8)
		self.bn1 = nn.BatchNorm2d(64)
		s = self.compute_conv_output_size(size, size // 8)
		s = s // 2
		self.conv2 = torch.nn.Conv2d(64, 128, kernel_size=size // 10)
		self.bn2 = nn.BatchNorm2d(128)
		s = self.compute_conv_output_size(s, size // 10)
		s = s // 2
		self.conv3 = torch.nn.Conv2d(128, 256, kernel_size=2)
		self.bn3 = nn.BatchNorm2d(256)
		s = self.compute_conv_output_size(s, 2)
		s = s // 2
		self.maxpool = torch.nn.MaxPool2d(2)
		self.relu = torch.nn.ReLU()

		self.drop1 = torch.nn.Dropout(0.2)
		self.drop2 = torch.nn.Dropout(0.5)
		self.fc1 = torch.nn.Linear(256 * s * s, 2048)
		self.bn4 = nn.BatchNorm1d(2048)
		self.fc2 = torch.nn.Linear(2048, 2048)
		self.bn5 = nn.BatchNorm1d(2048)
		self.linear = nn.Linear(2048, self.total_classes)

	def compute_conv_output_size(self, Lin, kernel_size, stride=1, padding=0, dilation=1):
		return int(np.floor((Lin + 2 * padding - dilation * (kernel_size - 1) - 1) / float(stride) + 1))

	def forward(self, x, task_id):
		h = self.maxpool(self.drop1(self.relu((self.conv1(x)))))
		h = self.maxpool(self.drop1(self.relu((self.conv2(h)))))
		h = self.maxpool(self.drop2(self.relu((self.conv3(h)))))
		h = h.view(x.size(0), -1)
		h = self.drop2(self.relu((self.fc1(h))))
		h = self.drop2(self.relu((self.fc2(h))))
		out = self.linear(h)
		if task_id is None:
			return out
		offset1 = int((task_id - 1) * self.n_classes)
		offset2 = int(task_id * self.n_classes)
		if offset1 > 0:
			out[:, :offset1].data.fill_(-10e10)
		if offset2 < self.total_classes:
			out[:, offset2:self.total_classes].data.fill_(-10e10)
		return out


class LeNet(nn.Module):
	"""
	LeNet model for OGD purposes
	Refer: https://github.com/MehdiAbbanaBennani/continual-learning-ogdplus/blob/master/models/lenet.py
	"""
	def __init__(self, out_dim, classes_per_task, in_channel=1, img_sz=32, hidden_dim=500):
		super(LeNet, self).__init__()
		feat_map_sz = img_sz // 4
		self.n_feat = 50 * feat_map_sz * feat_map_sz
		self.hidden_dim = hidden_dim
		self.n_classes =  classes_per_task
		self.total_classes = out_dim
		self.linear = nn.Sequential(
			nn.Conv2d(in_channel, 20, 5, padding=2),
			nn.BatchNorm2d(20),
			nn.ReLU(inplace=True),
			nn.MaxPool2d(2, 2),
			nn.Conv2d(20, 50, 5, padding=2),
			nn.BatchNorm2d(50),
			nn.ReLU(inplace=True),
			nn.MaxPool2d(2, 2),
			nn.Flatten(),
			nn.Linear(self.n_feat, hidden_dim),
			# nn.BatchNorm1d(hidden_dim),
			nn.ReLU(inplace=True),
		)

		self.last = nn.Linear(hidden_dim, out_dim)  # Subject to be replaced dependent on task

	def features(self, x):
		# x = self.conv(x)
		# x = self.linear(x.view(-1, self.n_feat))
		return self.linear(x)

	def logits(self, x):
		x = self.last(x)
		return x

	def forward(self, x, task_id=None):
		x = self.features(x)
		out = self.logits(x)
		if task_id is None:
			return out
		offset1 = int((task_id - 1) * self.n_classes)
		offset2 = int(task_id * self.n_classes)
		if offset1 > 0:
			out[:, :offset1].data.fill_(-10e10)
		if offset2 < self.total_classes:
			out[:, offset2:self.total_classes].data.fill_(-10e10)
		return out


def LeNetC(hidden_dim, classes_per_task, out_dim=100):  # LeNet with color input
	return LeNet(out_dim=out_dim, classes_per_task=classes_per_task, in_channel=3, img_sz=32, hidden_dim=hidden_dim)