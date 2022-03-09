from importlib.resources import path
import cv2 as cv
import numpy as np
import glob
import open3d as o3d
import copy

# from o3d.geometry.PointCloud import create_from_rgbd_image
# from o3d.pipelines.registration import registration_icp

class Modeler:
    VOXEL_SIZE = 0.0000001
    M = 100
    N = 100

    def __init__(self, rgb_path, depth_path):
        self.pc_model = None
        self.mesh_model = None
        self.rgb = glob.glob(rgb_path + '*.jpg')
        self.rgb.sort()
        self.depth = glob.glob(depth_path + '*.png')
        self.depth.sort()
        print(str(len(self.rgb)) + ' found in folder')
    
    def create_model(self):
        # MAX = 10
        # s_rgb = self.rgb[:MAX]
        # s_depth = self.depth[:MAX]
        s_rgb = self.__get_sample(self.rgb,10,10)
        s_depth = self.__get_sample(self.depth,10,10)
        s_rgb = self.__load_rgbs(s_rgb)
        s_depth = self.__load_depths(s_depth)
        s_depth = self.__segment_objects(s_depth)
        s_rgbd = self.__create_rgbd(s_rgb,s_depth)
        self.__create_pc_model(s_rgbd)
        # self.__create_mesh_model(self.pc_model)

    def save_pc_model(self, fn):
        print('saving pc model...')
        o3d.io.write_point_cloud(fn,self.pc_model,
                        write_ascii=False,compressed=True,print_progress=True)
        print('pc model saved')

    def __get_sample(self,paths,jump,max):
        sample = []
        i = 0
        count = 0
        size = len(paths)
        while i<size and count<max:
            sample.append(paths[i])
            i += jump
            count += 1
        return sample
    
    def __create_mesh_model(self, pcd):
        #Vertex DownSampling 
        print("Downsample the point cloud with a voxel of 0.000001")
        downpcd = pcd.voxel_down_sample(voxel_size=0.000001)
        #downpcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        #adding normals
        print("Adding the normals on the Point cloud and Invalidates Existing normals")
        downpcd.normals = o3d.utility.Vector3dVector(np.zeros((1, 3)))  # invalidate existing normals
        print("Estimating normals")
        downpcd.estimate_normals()
        downpcd.orient_normals_consistent_tangent_plane(100)
        #creating Alpha mesh
        print("Creating the mesh using Alpha model")
        meshAlpha = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(downpcd,0.03)
        meshAlpha.compute_triangle_normals(normalized=True)
        #displaying of model
        print("Displaying the Mesh")
        o3d.visualization.draw_geometries([meshAlpha], mesh_show_back_face=True)
        self.mesh_model = meshAlpha

    
    def __create_pc_model(self,s_rgbd):
        param1 = o3d.camera.PinholeCameraIntrinsic(o3d.camera.PinholeCameraIntrinsicParameters.PrimeSenseDefault)
        param2 = o3d.pipelines.registration.TransformationEstimationPointToPoint()

        threshold = 0.002
        transform = np.asarray([[1.0, 0.0, 0.0, 0.0],
                                [0.0, -1.0, 0.0, 0.0],
                                [0.0, 0.0, -1.0, 0.0], 
                                [0.0, 0.0, 0.0, 1.0]])

        count = 1
        size = len(s_rgbd)

        print('creating model', '[' + str(count) + '/' + str(size) + ']')
        count += 1
        target = o3d.geometry.PointCloud.create_from_rgbd_image(s_rgbd.pop(0),param1)
        target = target.voxel_down_sample(voxel_size=self.VOXEL_SIZE)
        target.transform(transform)
        print(len(target.points))
        # o3d.visualization.draw_geometries([target])
        
        # pcd = [target]

        for rgbd in s_rgbd:
            print('creating model', '[' + str(count) + '/' + str(size) + ']')
            count += 1
            source = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd,param1)
            source = source.voxel_down_sample(voxel_size=self.VOXEL_SIZE)
            reg_p2p = o3d.pipelines.registration.registration_icp(source, target, threshold, transform, param2)
            transform = reg_p2p.transformation
            evaluation = o3d.pipelines.registration.evaluate_registration(source, target,
                                                    threshold, transform)
            # self.__draw_registration_result(source,target,transform)
            source.transform(transform)
            # pcd.append(source)
            # o3d.visualization.draw_geometries([source])
            # target = self.__combine(source,target)
            # self.__fuse(source,target,transform)
            target = target + source
            target = target.voxel_down_sample(voxel_size=self.VOXEL_SIZE)
            print(evaluation.fitness, len(target.points))
            # print(np.asarray(evaluation.correspondence_set))
            
        
        o3d.visualization.draw_geometries([target])
        # o3d.visualization.draw_geometries(pcd)
        self.pc_model = target
        print(target)

    def __fuse(self, source, target, transform):
        for p in source:
            p = p.transform(transform)
            target += p

    def __combine(self, source, target):
        source = np.asarray(source)
        target = np.asarray(target)
        print(source.shape,target.shape)
        combined = self.__union_points(source, target)
        combined = o3d.geometry.Image(combined.astype(np.uint8))
        return combined

    def __union_points(self, arr1, arr2):
        mask = []
        count = 0
        for p2 in arr2:
            flag = False
            for p1 in arr1:
                if self.__is_points_equal(p1,p2):
                    count += 1
                    flag = True
                    print('same point detected', 'count: ' + str(count))
                    break
            mask.append(flag)
        mask = np.asarray(mask)
        arr1 = arr1[mask]
        return np.concatenate((arr1,arr2), axis=0)

    def __is_points_equal(self, p1, p2):
        d = (p1[0]-p2[0])**2
        d += (p1[1]-p2[1])**2
        d += (p1[2]-p2[2])**2
        return d < 0.001
    
    def __draw_registration_result(self, source, target, transformation):
        source_temp = copy.deepcopy(source)
        target_temp = copy.deepcopy(target)
        # source_temp.paint_uniform_color([1, 0.706, 0])
        target_temp.paint_uniform_color([0, 0.651, 0.929])
        source_temp.transform(transformation)
        o3d.visualization.draw_geometries([source_temp, target_temp])

    def __create_rgbd(self,rgbs,depths):
        imgs = []
        rgbds = [(rgb,d) for (rgb,d) in zip(rgbs, depths)]
        count = 1
        size = len(rgbs)
        for rgbd in rgbds:
            print('creating RGBD images', '[' + str(count) + '/' + str(size) + ']')
            count+=1
            img = o3d.geometry.RGBDImage.create_from_color_and_depth(rgbd[0], rgbd[1])
            imgs.append(img)
        return imgs

    def __load_rgbs(self, objs):
        imgs = []
        count = 1
        size = len(objs)
        for obj in objs:
            print('loading depth images', '[' + str(count) + '/' + str(size) + ']')
            count+=1
            img = o3d.io.read_image(obj)
            imgs.append(img)
        return imgs

    def __load_depths(self, depths):
        imgs = []
        count = 1
        size = len(depths)
        for depth in depths:
            print('loading depth images', '[' + str(count) + '/' + str(size) + ']')
            count+=1
            img = cv.imread(depth)[:,:,0]
            imgs.append(img)
        return imgs

    def __segment_objects(self, depths):
        thresholds = []
        obj_depths = []
        count = 1
        size = len(depths)
        for img in depths:
            print('segmenting object depths', '[' + str(count) + '/' + str(size) + ']')
            count+=1
            tiles = [img[x:x+self.M,y:y+self.N] for x in range(0,img.shape[0],self.M) for y in range(0,img.shape[1],self.N)]
            th = set()
            for tile in tiles:
                t = self.__get_global_threshold(tile)
                # print('t =', t)
                th.add(t)
            th = list(th)
            th.sort(reverse=True)
            if len(th)!=1 and th[0]==255: th.pop(0)
            # print('th =', th)
            thresholds.append(th[0])
            self.__extract_obj(img,th[0])
            img = o3d.geometry.Image(img.astype(np.uint8))
            obj_depths.append(img)
        print('Segments Set Summary:', set(thresholds))
        return obj_depths
    
    def __extract_obj(self, img, t):
        img[img>t] = 0
    
    def __get_initial_threshold(self, img):
        h, _ = np.histogram(a=img, bins=256, range=(0,255))
        h[0] = 0
        m = 1
        n = 255
        while m<n and h[m]==0:
            m+=1
        while n>m and h[n]==0:
            n-=1
        return (m+n)//2

    def __get_global_threshold(self, img):
        t0 = 255
        t1 = self.__get_initial_threshold(img)
        # print('t1 =', t1)
        while t1 < t0:
            m1 = img > t1
            m2 = img <= t1
            r1 = img[m1]
            r2 = img[m2]
            s1 = np.size(r1)
            s2 = np.size(r2)
            if s1==0 or s2==0:
                t1 = t0
                break
            else:
                mean1 = np.sum(r1)//np.size(r1)
                mean2 = np.sum(r2)//np.size(r2)
                t0 = t1
                t1 = (mean1 + mean2)//2
        return int(t1)