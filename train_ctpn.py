# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import os
os.environ['MXNET_CUDNN_AUTOTUNE_DEFAULT']='0'

import argparse
import mxnet as mx

from rcnn.logger import logger
from rcnn.config import config, default, generate_config

'''
  here main training part can be present
'''
from rcnn.tools.train_rpn import train_rpn
from rcnn.tools.test_rpn import test_rpn
from rcnn.tools.train_rcnn import train_rcnn
from rcnn.utils.combine_model import combine_model


def alternate_train(args, ctx, pretrained, epoch,
                    rpn_epoch, rpn_lr, rpn_lr_step):
    # basic config
    begin_epoch = 0
    config.TRAIN.BG_THRESH_LO = 0.0

    logger.info('########## TRAIN RPN WITH IMAGENET INIT')
    train_rpn(args.network, args.dataset, args.image_set, args.root_path, args.dataset_path,
              args.frequent, args.kvstore, args.work_load_list, args.no_flip, args.no_shuffle, args.resume,
              ctx, pretrained, epoch, 'model/rpn1', begin_epoch, rpn_epoch,
              train_shared=False, lr=rpn_lr, lr_step=rpn_lr_step)

def parse_args():
    parser = argparse.ArgumentParser(description='Train Faster R-CNN Network')
    # general
    parser.add_argument('--network', help='network name', default=default.network, type=str)
    parser.add_argument('--dataset', help='dataset name', default=default.dataset, type=str)
    args, rest = parser.parse_known_args()
    generate_config(args.network, args.dataset)
    parser.add_argument('--image_set', help='image_set name', default=default.image_set, type=str)
    parser.add_argument('--root_path', help='output data folder', default=default.root_path, type=str)
    parser.add_argument('--dataset_path', help='dataset path', default=default.dataset_path, type=str)
    # training
    parser.add_argument('--frequent', help='frequency of logging', default=default.frequent, type=int)
    parser.add_argument('--kvstore', help='the kv-store type', default=default.kvstore, type=str)
    parser.add_argument('--work_load_list', help='work load for different devices', default=None, type=list)
    parser.add_argument('--no_flip', help='disable flip images', default=0, type=int)
    parser.add_argument('--no_shuffle', help='disable random shuffle', action='store_true')
    parser.add_argument('--resume', help='continue training', action='store_true')
    # alternate
    parser.add_argument('--gpus', help='GPU device to train with', default='0', type=str)
    parser.add_argument('--pretrained', help='pretrained model prefix', default=default.pretrained, type=str)
    parser.add_argument('--pretrained_epoch', help='pretrained model epoch', default=default.pretrained_epoch, type=int)
    parser.add_argument('--rpn_epoch', help='end epoch of rpn training', default=default.rpn_epoch, type=int)
    parser.add_argument('--rpn_lr', help='base learning rate', default=default.rpn_lr, type=float)
    parser.add_argument('--rpn_lr_step', help='learning rate steps (in epoch)', default=default.rpn_lr_step, type=str)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    logger.info('Called with argument: %s' % args)
    ctx = [mx.gpu(int(i)) for i in args.gpus.split(',')]
    alternate_train(args, ctx, args.pretrained, args.pretrained_epoch,
                    args.rpn_epoch, args.rpn_lr, args.rpn_lr_step)

if __name__ == '__main__':
    main()
