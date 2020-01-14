
## 1. fully supervised learning
python Train_Supervised.py --use_gpu 0 --labels all
python Train_Supervised.py --use_gpu 0 --labels 4000

## 2. UDA 
python Train_Semi_Supervised.py --use_gpu 0 --labels 4000
python Train_Semi_Supervised.py --use_gpu 0 --labels 4000 --tsa linear_schedule --softmax-temp 0.5 --confidence-mask 0.6
python Train_Semi_Supervised.py --use_gpu 0 --labels 250 --softmax-temp 0.5 --confidence-mask 0.6

