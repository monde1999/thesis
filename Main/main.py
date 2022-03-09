print('starting...')

from modeler import Modeler

def main():
    rgb = '../../dataset/rgb/'
    depth = '../../dataset/depth/'
    modeler = Modeler(rgb,depth)
    modeler.create_model()
    modeler.save_pc_model('model.pcd')

if __name__ == '__main__':
    main()