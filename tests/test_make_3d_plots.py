#!/usr/bin/env python
#file test_make_3d_plots.py

__author__ = "Jesse Stombaugh"
__copyright__ = "Copyright 2011, The QIIME Project" #consider project name
__credits__ = ["Jesse Stombaugh", "Dan Knights", "Antonio Gonzalez Pena", \
                "Yoshiki Vazquez Baeza"] #remember to add yourself
__license__ = "GPL"
__version__ = "1.5.0-dev"
__maintainer__ = "Jesse Stombaugh"
__email__ = "jesse.stombaugh@colorado.edu"
__status__ = "Development"

from numpy import array, nan, diff
from StringIO import StringIO
from os.path import exists
from cogent.util.unit_test import TestCase, main
from os import remove, mkdir, system
from random import choice, randrange, random
import shutil
from qiime.colors import data_colors
from qiime.make_3d_plots import (make_3d_plots,scale_pc_data_matrix,
                                    auto_radius,make_mage_output,
                                    get_coord,natsort,process_custom_axes, 
                                    get_custom_coords,remove_nans,
                                    scale_custom_coords,remove_unmapped_samples,
                                    make_edges_output,make_ellipsoid_faces,
                                    make_mage_ellipsoids,subdivide,
                                    get_multiple_coords,validate_coord_files,
                                    make_3d_plots_invue, make_vectors_output, 
                                    make_subgroup_vectors, 
                                    run_ANOVA_trajetories,
                                    generate_3d_plots, 
                                    can_run_ANOVA_trajectories,
                                    avg_vector_for_group,
                                    weight_by_vector,
                                    windowed_diff)
from qiime.util import get_tmp_filename

class TopLevelTests(TestCase):
    """Tests of top-level functions"""

    def setUp(self):
        """define some top-level data"""
        self.data={}
        self.data['coord']=[['Sample1','Sample2'],array([[-0.2,0.07],\
                            [-0.04,0.2]]),array([0.7,0.6]),\
                            array([25.00,30.00])]
        self.data['map']=[['#Sample-ID','Day'],['Sample1','Day1'],['Sample2',\
                            'Day1']]
        self.coord_header=["Sample1","Sample2","Sample3"]
        self.coords=array([[-0.219044992,0.079674486,0.09233683],[-0.042258081,\
                        0.000204041,0.024837603],[0.080504323,-0.212014503,\
                        -0.088353435]])
        self.groups={}
        self.groups['Day1']=['Sample1','Sample2','Sample3']
        self.colors={}
        self.colors['Day1']='blue1'
        self.pct_var=array([25.00,30.00,35.00])
        self.coord_tups = [("1", "2"), ("3", "2"), ("1", "3")]
        self.colors={"Day1":"blue1"}
        self.filename='test_pca.txt'
        self.dir_path='/tmp/' 
        self.prefs={}
        self.prefs['Sample']={}   
        self.prefs['Sample']['column']="Day"
        self.background_color='black'
        self.label_color='white'
        self.mapping=[["Sample-ID","Day","Type"],["Sample1","Day1","Soil"],\
                    ["Sample2","Day1","Soil"],["Sample3","Day1","Soil"]]
        self.mapping2=[["Sample-ID","Day","Type","Height","Weight"],\
                        ["Sample1","Day1","Soil","10","60"],\
                        ["Sample2","Day1","Soil","20","55"],\
                        ["Sample3","Day1","Soil","30","50"]]
        self.axis_names = 'Height,Weight'
        self._paths_to_clean_up = []
        self._dir_to_clean_up = ''

        self.prefs_vectors={}
        self.prefs_vectors['Sample']={}   
        self.prefs_vectors['Sample']['column']="Type"
        self.coords2 = array([[0, -0.219044992,0.079674486,0.09233683], \
                                [1, -0.042258081, 0.000204041, 0.024837603],\
                                [2, 0.080504323, -0.212014503, -0.088353435],\
                                [3, 0.012345551, -0.124512513, -01142356135]])
        self.custom_axes = ['Height']
        self.add_vectors = {'vectors_algorithm': 'trajectory', 'vectors_axes': 3,\
                                'vectors': ['Height'], 'vectors_path': 'vectors_test',\
                                'eigvals': array([ 0, 2.44923871, 1.11678013, 1.01533255]),\
                                'vectors_output': {},\
                                'weight_by_vector' : False,\
                                'window_size': 1}
        self.filename_vectors = 'vectors_test'
        self.file_path_vectors = 'vectors_test_dir'

        self.data_vectors = {}
        self.data_vectors['coord'] = \
            [["Sample1","Sample2","Sample3","Sample4"],self.coords2, \
            self.add_vectors['eigvals'], self.pct_var, None, None]
        self.data_vectors['map'] = [["Sample-ID","Height","Type","Weight"],\
                            ["Sample1","10","Soil_A","60"],\
                            ["Sample2","20","Soil_A","55"],\
                            ["Sample3","30","Soil_B","50"],\
                            ["Sample4","40","Soil_B","55"]]

        # data for test_can_run_ANOVA_trajectories
        self.anova_dict_true = {'first group' : [1, 2, 3, 4, 5, 6, 7],\
            'second group' : [1, 2, 3, 4, 5, 6, 7],\
            'third group' : [1, 2, 3, 4, 5, 6, 7],\
            'fourth group' : [1, 2, 3, 4, 5, 6, 7],}
        self.anova_dict_false = {'first group' : [1], 'second group' : [2],\
            'third group' : [3], 'fourth group' : [4]}
            
        # data test_avg_vector_for_group
        self.in_avg_group_name = '14655'
        self.in_avg_ids = ['FL.3.16a.281887', 'FL.3.16a.281888',\
            'FL.3.16a.281890', 'FL.3.16a.281891']
        self.in_avg_coord_dict = {\
            'FL.3.16a.281887':array([1, 2, 3, 4]),\
            'FL.3.16a.281888':array([2, 4, 6, 8]),\
            'FL.3.16a.281890':array([1, 7, 2, 1]),\
            'FL.3.16a.281891':array([2, 7, 2, 1]),}
        self.in_avg_custom_axes = ['days_since_epoch']
        self.in_avg_add_vectors = {'vectors_path': 'vectors_output.txt',\
            'vectors_algorithm': None,\
            'vectors': {'FL_R17': [('14424', 'FL.3.16a.281887'),\
            ('14435', 'FL.3.16a.281888')],\
            'FL_R18': [('14424', 'FL.3.16a.281890'),\
            ('14435', 'FL.3.16a.281891')]}}
        self.out_avg_coord_dict = {\
            '14435' : array([2, 5.5, 4.0, 4.5]),\
            '14424' : array([1, 4.5, 2.5, 2.5])}
        self.out_avg_add_vectors = {'vectors_path':'vectors_output.txt',\
            'vectors_algorithm': None,\
            'vectors':\
            {'14655': [('0', '14424'),\
            ('1', '14435')]}}

    def tearDown(self):
        map(remove,self._paths_to_clean_up)
        if self._dir_to_clean_up != '':
            shutil.rmtree(self._dir_to_clean_up)

    def test_make_3d_plots(self):
        """make_3d_plots: main script to create kinemage and html file"""
        obs_kin=make_3d_plots(self.coord_header,self.coords,self.pct_var, \
                        self.mapping,self.prefs,self.background_color, \
                        self.label_color,plot_scaled=True,plot_unscaled=True)

        self.assertEqual(obs_kin,exp_kin_full)

        # test with custom axes
        custom_axes = ['Height','Weight']
        coord_data = array([[10,60,-0.219044992,0.079674486,0.09233683],
                            [20,55,-0.042258081, 0.000204041,0.024837603],
                            [30,50,0.080504323,-0.212014503,-0.088353435]])
        coords = [self.coord_header, coord_data]
        scale_custom_coords(custom_axes,coords) 
        obs_kin=make_3d_plots(self.coord_header,coords[1],self.pct_var, \
                            self.mapping2,self.prefs,self.background_color,\
                            self.label_color,custom_axes=custom_axes, \
                            plot_scaled=True,plot_unscaled=True)
        self.assertEqual(obs_kin, exp_kin_full_axes)
        
        # test with custom axes and vector creation
        obs_kin = make_3d_plots(self.coord_header, self.coords2, self.pct_var, \
                            self.mapping2, self.prefs, self.background_color, \
                            self.label_color, custom_axes=self.custom_axes, \
                            add_vectors=self.add_vectors)
        self.assertEqual(obs_kin, exp_kin_vectors)

        # test with multiple 'colorby' columns to ensure sorting
        newprefs = {}
        newprefs['Type']={}   
        newprefs['Type']['column']="Type"
        newprefs['Day']={}   
        newprefs['Day']['column']="Day"
        obs_kin=make_3d_plots(self.coord_header,self.coords,self.pct_var, \
                            self.mapping,newprefs,self.background_color, \
                            self.label_color,plot_scaled=True,plot_unscaled=True)
        text = '\n'.join(obs_kin)
        
        self.assertTrue(text.find('Day_unscaled') < text.find('Type_unscaled'))
        
        # test with unscaled only
        obs_kin=make_3d_plots(self.coord_header,self.coords,self.pct_var, \
                        self.mapping,newprefs,self.background_color, \
                        self.label_color,plot_scaled=False,plot_unscaled=True)
        text = '\n'.join(obs_kin)
        
        self.assertTrue(text.find('Day_unscaled')>0)
        self.assertFalse(text.find('Day_scaled')>0)
        
        # test with scaled only
        obs_kin=make_3d_plots(self.coord_header,self.coords,self.pct_var, \
                        self.mapping,newprefs,self.background_color, \
                        self.label_color,plot_scaled=True,plot_unscaled=False)
        text = '\n'.join(obs_kin)
        
        self.assertFalse(text.find('Day_unscaled')>0)
        self.assertTrue(text.find('Day_scaled')>0)

 
        """make_3d_plots_invue: main script to create invue files"""
        data = {'map': [
                    ['SampleID', 'Treatment'], ['PC.354', 'Control'], ['PC.355', 'Control'], 
                    ['PC.607', 'Fast']], 
                'coord': [['PC.354', 'PC.355', 'PC.607',],
                array([[ -2.93088213e-01,   4.31583200e-02,  -6.10931011e-02, 
                    -4.45457646e-02,   1.83903403e-01,   5.62150139e-02, 
                    1.05297152e-01,   2.13883515e-01,  -5.71356497e-09],
                    [-2.09986576e-01,  -2.20253966e-01,   3.20511936e-02,
                    8.55386819e-02,  -2.25272826e-01,  -4.17365121e-02,
                    1.99893660e-01,  -4.00712898e-02,  -5.71356497e-09],
                    [1.08572516e-01,   3.82643187e-01,   2.15202408e-01,
                    1.05970644e-01,  -1.22775938e-01,  -2.16486387e-02, 
                    7.14806423e-03,   5.56601903e-02,  -5.71356497e-09]]), 
                array([  4.95533900e-01,   2.89252050e-01,   1.52106359e-01]),
                array([  2.72623936e+01,   1.59135495e+01,   8.36831432e+00,]), None, None]}
        groups_and_colors = [('Treatment', {'Control': ['PC.354', 'PC.355'], 'Fast': ['PC.607']}, 
            {'Control': 'blue1', 'Fast': 'red1'}, data_colors, data_colors.keys())]
        intp_pts = 2
        
        smp_lbl_exp = {'Treatment': {
                        'coords': [array([ -2.93088213e-01,   4.31583200e-02,  -6.10931011e-02,
                                    2.55000000e+02]), array([ -2.09986576e-01,  -2.20253966e-01,   
                                    3.20511936e-02, 2.55000000e+02]), array([  1.08572516e-01,
                                    3.82643187e-01,   2.15202408e-01, 6.52800000e+04])], 
                        'headrs': ['PC.354', 'PC.355', 'PC.607']}
                      }
        smp_lbl_grp_exp = {'Treatment': {
                        'Control': {
                            'coords': [array([-0.29308821,  0.04315832, -0.0610931 ]), 
                                    array([-0.26538767, -0.04464578, -0.030045  ]),
                                    array([-0.23768712, -0.13244987,  0.0010031 ]), 
                                    array([-0.20998658, -0.22025397,  0.03205119])], 
                            'headrs': ['PC.354', 'PC.355.0', 'PC.355.1', 'PC.355.2']}, 
                        'Fast': {
                            'coords': [array([ 0.10857252,  0.38264319,  0.21520241])], 
                            'headrs': ['PC.607']
                                }
                        }}
        poly_pts_exp = array([[0.16285877,0.57396478,0.32280361],\
            [-0.31497986,-0.33038095,0.04807679],[-0.31497986,-0.33038095,0.04807679],\
            [0.16285877,0.57396478,0.32280361],[0.16285877,0.57396478,0.32280361],\
            [-0.31497986,-0.33038095,0.04807679],[-0.31497986,-0.33038095,0.04807679]])
                      
        smp_lbl, smp_lbl_grp, poly_pts = make_3d_plots_invue(data, groups_and_colors, intp_pts, \
            polyh_pts=4, offset=1.5)
        
        self.assertFloatEqual(smp_lbl['Treatment']['coords'],smp_lbl_exp['Treatment']['coords'], 16711680.0)
        self.assertFloatEqual(smp_lbl_grp['Treatment']['Control']['coords'],\
                  smp_lbl_grp_exp['Treatment']['Control']['coords'], 16711680.0)
        self.assertFloatEqual(poly_pts,poly_pts_exp)

    def test_generate_3d_plots(self):
        """generate_3d_plots: Writes the output of make_3d_plots into a file"""
        # Tests could have failed prior to this execution, therefore check if
        # any of the following dirs exist already and try to remove them
        try:
            shutil.rmtree(self.file_path_vectors)
            remove(self.filename_vectors)
            remove('vectors_raw_values.txt')
            remove("{0}_3D_PCoA_plots.html".format(self.filename_vectors))
        except OSError:
            pass

        # Create a dir for the vector files
        mkdir(self.file_path_vectors)

        generate_3d_plots(self.prefs_vectors, self.data_vectors, self.custom_axes, self.background_color, \
                        self.label_color, data_file_path=self.file_path_vectors, \
                        filename=self.filename_vectors, add_vectors=self.add_vectors)

        # Check that the files are created
        self.assertTrue(exists(self.filename_vectors))
        self.assertTrue(exists("{0}_3D_PCoA_plots.html".format(self.filename_vectors)))

        # Remove the temp directory and all the other files
        shutil.rmtree(self.file_path_vectors)
        remove(self.filename_vectors)
        remove('vectors_raw_values.txt')
        remove("{0}_3D_PCoA_plots.html".format(self.filename_vectors))

    def test_scale_pc_data_matrix(self):
        """scale_pc_data_matrix: Scales the pc data for use in the 3d plots"""
        exp=array([[-1.56460709e-01,6.82924166e-02,9.23368300e-02],\
                    [-3.01843436e-02,1.74892286e-04,2.48376030e-02],\
                    [5.75030879e-02,-1.81726717e-01,-8.83534350e-02]])

        obs=scale_pc_data_matrix(self.coords, self.pct_var)

        self.assertFloatEqual(obs,exp)
  
    def test_auto_radius(self):
        """auto_radius: determines the radius for the circles in the plot"""
        exp=array([0.00299549315])

        obs=auto_radius(self.coords)

        self.assertFloatEqual(obs,exp)
    
    def test_make_mage_output(self):
        """make_mage_output: Create kinemage string given the data"""
        # test without custom axes
        obs_kin=make_mage_output(self.groups,self.colors,self.coord_header,\
                                self.coords,self.pct_var,self.background_color,\
                                self.label_color,data_colors)
        self.assertEqual(obs_kin,exp_kin_partial)

        # test with custom axes
        custom_axes = ['Height','Weight']
        coord_data = array([[10,60,-0.219044992,0.079674486,0.09233683],
                            [20,55,-0.042258081, 0.000204041,0.024837603],
                            [30,50,0.080504323,-0.212014503,-0.088353435]])
        coords = [self.coord_header, coord_data]
        scale_custom_coords(custom_axes,coords)
        obs_kin=make_mage_output(self.groups,self.colors,self.coord_header,\
                                coords[1],self.pct_var,self.background_color, \
                                self.label_color,data_colors,
                                custom_axes=custom_axes)
        self.assertEqual(obs_kin, exp_kin_partial_axes)

    def test_make_edge_output(self):
        """make_edge_output: Create kinemage string given the data"""
        # test without custom axes
        exp_result = ['@vectorlist {edges} dimension=4 on master={edges} nobutton', '1.0 2.0 3.0 4.0 white', '1.06 2.06 3.06 4.06 white P', '1.06 2.06 3.06 4.06 hotpink', '1.1 2.1 3.1 4.1 hotpink P', '1.0 2.0 3.0 4.0 white', '1.12 2.12 3.12 4.12 white P', '1.12 2.12 3.12 4.12 hotpink', '1.2 2.2 3.2 4.2 hotpink P']
        edges = [['a_0','a_1'],['a_0','a_2']]
        coord_dict = {}
        coord_dict['a_0'] = array([ 1.0, 2.0, 3.0, 4.0])
        coord_dict['a_1'] = array([ 1.1, 2.1, 3.1, 4.1])
        coord_dict['a_2'] = array([ 1.2, 2.2, 3.2, 4.2])
        num_coords=4
        arrow_colors={'line_color': 'white', 'head_color': 'hotpink'}
        obs_result=make_edges_output(coord_dict, edges, num_coords, \
                        self.label_color, arrow_colors=arrow_colors)
        
        self.assertEqual(obs_result, exp_result)
  
    def test_make_vectors_output(self):
        """make_vectors_output: Create kinemage string given the data"""
        vectors = {'vectors': {'test': [('1', 'a_0'), ('2', 'a_1'), ('3', 'a_0')]}}
        coord_dict = {}
        coord_dict['a_0'] = array([ 1.0, 2.0, 3.0, 4.0])
        coord_dict['a_1'] = array([ 1.1, 2.1, 3.1, 4.1])
        coord_dict['a_2'] = array([ 1.2, 2.2, 3.2, 4.2])
        num_coords=4
        color = 'hotpink'
        ids = ['a_0']
        
        # test without custom axes
        exp_result = ['@vectorlist {trace} dimension=4 on', \
            '1.0 2.0 3.0 4.0 hotpink', \
            '1.05 2.05 3.05 4.05 hotpink P', \
            '1.05 2.05 3.05 4.05 hotpink', \
            '1.1 2.1 3.1 4.1 hotpink P']
            
        obs_result=make_vectors_output(coord_dict, vectors, num_coords,\
            color, ids)
            
        self.assertEqual(obs_result, exp_result)
    
    def test_make_subgroup_vectors(self):
        """make_subgroup_vectors: Returns the correct vector based on groups
        per algorithm"""
        coord_dict = dict(zip(self.coord_header,self.coords))
        # eigvals values should go from high to low and pct_var goes from low to high
        eigvals = [i for i in reversed(self.pct_var)]
        ids = ['Sample1', 'Sample2', 'Sample3']

        # Testing rms
        exp_result = {'calc': {'avg':5.32480386489972}, \
                        'vector': [6.995474752449276, 1.5180408981614073, 7.4608959440884766],\
                        'message': None }
        self.assertFloatEqual(make_subgroup_vectors(coord_dict, eigvals, ids), exp_result)
        
        # Testing trajectory
        exp_result = {'calc': {'trajectory':15.92846773878855}, \
                        'vector': [14.383977976653455, 6.8423140875566384],\
                        'message': None }
        self.assertFloatEqual(make_subgroup_vectors(coord_dict, eigvals, ids, 'trajectory'), exp_result)

        # Testing first difference 
        exp_result = {'vector': array([-7.54166389]) , \
                        'calc': {'mean': [-7.541663889096816], 'std': [0.0]},\
                        'message': None }
        self.assertFloatEqual(make_subgroup_vectors(coord_dict, eigvals, ids, 'diff'), exp_result)

        # this test should return a message to print in the output file
        exp_result ={'vector': [-7.5416638890968164, 0.0], \
                        'message': None,
                        'calc': {
                            'std': 3.7708319445484082, 
                            'mean': -3.7708319445484082
                        }
                    }
        calc_result = make_subgroup_vectors(coord_dict, eigvals, ids, 'wdiff', window_size=1)
        self.assertEquals(calc_result, exp_result)
                      
    def test_run_ANOVA_trajetories(self):
        """run_ANOVA_trajetories: should return the same value
        """
        data = dict(zip(self.coord_header,self.coords))
        labels, groups_means, prob = run_ANOVA_trajetories(data)
        exp_labels = ['Sample1', 'Sample3', 'Sample2']
        exp_groups_means = [-0.015677892000000002, -0.073287871666666657, -0.0057388123333333334]
        exp_prob = 0.80674568762274179
                                     
        self.assertEqual(labels, exp_labels)
        self.assertFloatEqual(groups_means, exp_groups_means)
        self.assertFloatEqual(prob, exp_prob)        
    
    def test_process_custom_axes(self):
        """process_custom_axes: Parses the custom_axes \
        option from the command line"""
        exp = ['Height','Weight']
        obs=process_custom_axes(self.axis_names)
        self.assertEqual(obs,exp)

    def test_get_custom_coords(self):
        """get_custom_coords: Gets custom axis coords from the mapping file."""
        exp = 1
        custom_axes = ['Height','Weight']
        coords = [self.coord_header, self.coords]
        get_custom_coords(custom_axes, self.mapping2, coords)
        exp = array([[10,60,-0.219044992,0.079674486,0.09233683],
                           [20,55,-0.042258081, 0.000204041,0.024837603],
                           [30,50,0.080504323,-0.212014503,-0.088353435]])
        self.assertEqual(coords[1],exp)

    def test_scale_custom_coords(self):
        """scale_custom_coords: \
        Scales custom coordinates to match min/max of PC1"""
        custom_axes = ['Height','Weight']
        coord_data = array([[10,60,-0.219044992,0.079674486,0.09233683],
                            [20,55,-0.042258081, 0.000204041,0.024837603],
                            [30,50,0.080504323,-0.212014503,-0.088353435]])
        coords = [self.coord_header, coord_data]
        scale_custom_coords(custom_axes,coords)
        # calculate results
        mn = coord_data[2,].min()
        mx = coord_data[2,].max()
        h = array([10.0,20.0,30.0])
        h = (h-min(h))/(max(h)-min(h))
        h = h * (mx-mn) + mn
        w = array([60.0,55.0,50.0])
        w = (w-min(w))/(max(w)-min(w))
        w = w * (mx-mn) + mn
        exp = array([[h[0],w[0],-0.219044992,0.079674486,0.09233683],
                            [h[1],w[1],-0.042258081, 0.000204041,0.024837603],
                            [h[2],w[2],0.080504323,-0.212014503,-0.088353435]])
        self.assertEqual(coords[1],exp)

    def test_remove_nans(self):
        """remove_nans: Deletes any samples with NANs in their coordinates"""
        coord_data = array([[10,60,-0.219044992,0.079674486,0.09233683],
                            [20,55,-0.042258081, nan,0.024837603],
                            [30,50,0.080504323,-0.212014503,-0.088353435]])
        coords = [self.coord_header, coord_data]
        remove_nans(coords)

        exp_header = ["Sample1","Sample3"]
        exp_coords = array([[10,60,-0.219044992,0.079674486,0.09233683],
                            [30,50,0.080504323,-0.212014503,-0.088353435]])
        self.assertEqual(coords[0],exp_header)
        self.assertEqual(coords[1],exp_coords)


    def test_remove_unmapped_samples(self):
        """remove_unmapped_samples: \
        Removes any samples not present in mapping file"""
        coord_data = array([[10,60,-0.219044992,0.079674486,0.09233683],
                            [20,55,-0.042258081, nan,0.024837603],
                            [30,50,0.080504323,-0.212014503,-0.088353435]])
        coords = [self.coord_header, coord_data]
        # mapping without sample2
        mapping=[["Sample-ID","Day","Type","Height","Weight"],\
                               ["Sample1","Day1","Soil","10","60"],\
                               ["Sample3","Day1","Soil","30","50"]]
        remove_unmapped_samples(mapping, coords)
        exp_header = ["Sample1","Sample3"]
        exp_coords = array([[10,60,-0.219044992,0.079674486,0.09233683],
                           [30,50,0.080504323,-0.212014503,-0.088353435]])
        self.assertEqual(coords[0],exp_header)
        self.assertEqual(coords[1],exp_coords)
    
    def test_make_ellipsoid_faces(self):
        # test without scaling
        res =  make_ellipsoid_faces([0,0,0],[1,1,1],nsubdivs=0)
        res = [[tuple(["%.5f"%(aijk) for aijk in aij]) for aij in ai] \
                   for ai in res]
        exp = [[tuple(["%.5f"%(aijk) for aijk in aij]) for aij in ai] \
                   for ai in exp_make_ellipsoid_faces]
        self.assertEqual(res,exp)

        # test without scaling
        res =  make_ellipsoid_faces([-1,2,3],[.2,2,20],nsubdivs=0)
        res = [[tuple(["%.5f"%(aijk) for aijk in aij]) for aij in ai] \
                   for ai in res]
        exp = [[tuple(["%.5f"%(aijk) for aijk in aij]) for aij in ai] \
                   for ai in exp_make_ellipsoid_faces_transformed]
        self.assertEqual(res,exp)

    def test_make_mage_ellipsoids(self):
        ids = ['A','B']
        coord_dict = {'A':array([0,0,0]),'B':array([-1,2,3])}
        coord_low_dict = {'A':array([-.5,-.5,-.5]),'B':array([-.1,-1,-10])}
        coord_high_dict = {'A':array([.5,.5,.5]),'B':array([.1,1,10])}
        ellipsoid_prefs = {"smoothness":0,"alpha":.25}
        res = make_mage_ellipsoids(ids, coord_dict, coord_low_dict,
                                   coord_high_dict,"red1", ellipsoid_prefs)
        self.assertEqual(res,exp_make_mage_ellipsoids)

    def test_subdivide(self):
        res = subdivide((1,0,0),(0,1,0),(0,0,1))
        res = [tuple([tuple(["%.5f"%(aijk) for aijk in aij]) for aij in ai]) \
                   for ai in res]
        exp = [tuple([tuple(["%.5f"%(aijk) for aijk in aij]) for aij in ai]) \
                   for ai in exp_subdivide]
        self.assertEqual(res,exp)

    def test_get_multiple_coords(self):
        # create the temporary pc files
        pc_file_1 = '\n'.join(['pc vector number\t1\t2',
                               'A\t1.1\t2.2',
                               'B\t4.1\t4.2',
                               'C\t-.1\t-.2',
                               'eigvals\t0.52\t0.24',
                               '% variation explained\t25.12\t13.29'])
        pc_file_2 = '\n'.join(['pc vector number\t1\t2',
                               'A\t2.1\t3.2',
                               'B\t5.1\t6.2',
                               'C\t-1.1\t-2.2',
                               'eigvals\t0.32\t0.14',
                               '% variation explained\t20.11\t12.28'])

        edges_file = '\n'.join(['B A','B\t\t\t   \t\tC'])

        fp1 = get_tmp_filename()
        fp2 = get_tmp_filename()
        fp3 = get_tmp_filename()
        try:
            f1 = open(fp1,'w')
            f2 = open(fp2,'w')
            f3 = open(fp3,'w')
        except IOError, e:
            raise e,"Could not create temporary files: %s, %s" %(f1,f2, f3)
        
        f1.write(pc_file_1)
        f1.close()
        f2.write(pc_file_2)
        f2.close()
        f3.write(edges_file)
        f3.close()
        
        # test without custom edges
        exp_edges = [('A_0', 'A_1'), ('B_0', 'B_1'), ('C_0', 'C_1')]
        exp_coords = [['A_0', 'B_0', 'C_0', 'A_1', 'B_1', 'C_1'], 
                      array([[ 1.1,  2.2],
                             [ 4.1,  4.2],
                             [-0.1, -0.2],
                             [ 2.1,  3.2],
                             [ 5.1,  6.2],
                             [-1.1, -2.2]]), 
                      array([ 0.52,  0.24]), array([ 25.12,  13.29]),
                      None, None]
        edges, coords = get_multiple_coords([fp1,fp2])
        self.assertEqual(edges, exp_edges)
        self.assertEqual(coords, exp_coords)

        # test with custom edges
        exp_edges = [['B', 'A'], ['B', 'C']]
        exp_coords = [['A', 'B', 'C'],
                      array([[ 1.1,  2.2],
                             [ 4.1,  4.2],
                             [-0.1, -0.2]]), 
                      array([ 0.52,  0.24]), array([ 25.12,  13.29]),
                      None, None]
        edges, coords = get_multiple_coords([fp1], fp3)
        self.assertEqual(edges, exp_edges)
        self.assertEqual(coords, exp_coords)
        
        # clean up
        remove(fp1)
        remove(fp2)
        remove(fp3)

    def test_get_multiple_coords_serial(self):
        # create the temporary pc files
        pc_file_1 = '\n'.join(['pc vector number\t1\t2',
                                'A\t1.1\t2.2',
                                'B\t4.1\t4.2',
                                'C\t-.1\t-.2',
                                'eigvals\t0.52\t0.24',
                                '% variation explained\t25.12\t13.29'])
        pc_file_2 = '\n'.join(['pc vector number\t1\t2',
                                'A\t2.1\t3.2',
                                'B\t5.1\t6.2',
                                'C\t-1.1\t-2.2',
                                'eigvals\t0.32\t0.14',
                                '% variation explained\t20.11\t12.28'])
        pc_file_3 = '\n'.join(['pc vector number\t1\t2',
                                'A\t2.2\t3.3',
                                'B\t5.2\t6.3',
                                'C\t-1.2\t-2.3',
                                'eigvals\t0.34\t0.15',
                                '% variation explained\t10.11\t2.28'])

        fp1 = get_tmp_filename()
        fp2 = get_tmp_filename()
        fp3 = get_tmp_filename()
        try:
            f1 = open(fp1,'w')
            f2 = open(fp2,'w')
            f3 = open(fp3,'w')
        except IOError, e:
            raise e,"Could not create temporary files: %s, %s" %(f1,f2, f3)
        
        f1.write(pc_file_1)
        f1.close()
        f2.write(pc_file_2)
        f2.close()
        f3.write(pc_file_3)
        f3.close()
        
        # test without serial
        exp_edges = [('A_0', 'A_1'), ('A_0', 'A_2'), 
                    ('B_0', 'B_1'), ('B_0', 'B_2'),
                    ('C_0', 'C_1'),('C_0', 'C_2')
                    ]
        exp_coords = [['A_0', 'B_0', 'C_0',
                       'A_1', 'B_1', 'C_1',
                       'A_2', 'B_2', 'C_2'], 
                        array([[ 1.1,  2.2],
                            [ 4.1,  4.2],
                            [-0.1, -0.2],
                            [ 2.1,  3.2],
                            [ 5.1,  6.2],
                            [-1.1, -2.2],
                            [ 2.2,  3.3],
                            [ 5.2,  6.3],
                            [-1.2, -2.3]]), 
                        array([ 0.52,  0.24]), array([ 25.12,  13.29]),
                        None, None]
        edges, coords = get_multiple_coords([fp1,fp2,fp3],serial=False)
        self.assertEqual(edges, exp_edges)
        self.assertEqual(coords, exp_coords)

        # test with serial
        exp_edges = [('A_0', 'A_1'), ('A_1', 'A_2'),
                    ('B_0', 'B_1'), ('B_1', 'B_2'),
                    ('C_0', 'C_1'),('C_1', 'C_2')
                    ]
        edges, coords = get_multiple_coords([fp1,fp2,fp3],serial=True)
        self.assertEqual(edges, exp_edges)
        self.assertEqual(coords, exp_coords)

        # clean up
        remove(fp1)
        remove(fp2)
        remove(fp3)

    def test_validate_coord_files(self):
        """Verifies that validate_coord_files works correctly"""
        # create the temporary pc files
        # one line has 4 columns
        pc_file_1 = '\n'.join(['pc vector number\t1\t2',
                                'A\t1.1\t2.2',
                                'B\t4.1\t4.2',
                                'C\t-.1\t-.2',
                                'eigvals\t0.52\t0.24\t0.11',
                                '% variation explained\t25.12\t13.29'])
        # all lines have 3 columns
        pc_file_2 = '\n'.join(['pc vector number\t1\t2',
                                'A\t2.1\t3.2',
                                'B\t5.1\t6.2',
                                'C\t-1.1\t-2.2',
                                'eigvals\t0.32\t0.14',
                                '% variation explained\t20.11\t12.28'])
        # all lines have two columns
        pc_file_3 = '\n'.join(['pc vector number\t1',
                                'A\t2.1',
                                'B\t5.1',
                                'C\t-1.1',
                                'eigvals\t0.32',
                                '% variation explained\t20.11'])
        # all lines have 3 columns
        pc_file_4 = '\n'.join(['pc vector number\t1\t2',
                                'A\t1.1\t2.2',
                                'B\t4.1\t4.2',
                                'C\t-.1\t-.2',
                                'eigvals\t0.52\t0.24',
                                '% variation explained\t25.12\t13.29'])

        fp1 = get_tmp_filename()
        fp2 = get_tmp_filename()
        fp3 = get_tmp_filename()
        fp4 = get_tmp_filename()

        try:
            f1 = open(fp1,'w')
            f2 = open(fp2,'w')
            f3 = open(fp3,'w')
            f4 = open(fp4,'w')
        except IOError, e:
            raise e,"Could not create temporary files: %s, %s" %(f1,f2,f3,f4)
        
        f1.write(pc_file_1)
        f1.close()
        f2.write(pc_file_2)
        f2.close()
        f3.write(pc_file_3)
        f3.close()
        f4.write(pc_file_4)
        f4.close()
         
        # one file with internal inconsistency
        result = validate_coord_files(fp1)
        self.assertEqual(result, False)
        # one file has two columns, one has 3 
        result = validate_coord_files([fp2,fp3])
        self.assertEqual(result, False)
        # first file consistent, second file not
        result = validate_coord_files([fp2, fp1])
        self.assertEqual(result, False)
        # both files consistent
        result = validate_coord_files([fp2, fp4])
        self.assertEqual(result, True)
        
        
        # clean up
        remove(fp1)
        remove(fp2)
        remove(fp3)
        remove(fp4)


    def test_can_run_ANOVA_trajectories(self):
        """ Test for valid dicts to be passed"""
        self.assertTrue(can_run_ANOVA_trajectories(self.anova_dict_true))
        self.assertFalse(can_run_ANOVA_trajectories(self.anova_dict_false))

    def test_avg_vector_for_group(self):
        """ Create an average set of coordinates """

        test_avg_coord_dict, test_avg_add_vectors = \
            avg_vector_for_group(self.in_avg_group_name, self.in_avg_ids,\
                self.in_avg_coord_dict, self.in_avg_custom_axes,\
                self.in_avg_add_vectors)
        self.assertEqual(test_avg_coord_dict, self.out_avg_coord_dict)
        self.assertEqual(test_avg_add_vectors, self.out_avg_add_vectors)

    def test_weight_by_vector(self):
        """ Test that the vector is weighted by the given vector"""
        # data for test_weight_by_vector
        self.in_vector_to_weight = array([1, 2, 3, 4, 5, 6, 7, 8])
        self.in_weighting_vector = array([1, 5, 8, 12, 45, 80, 85, 90])
        self.out_weighted_vector = array([1, 6.3571428571428568,\
            12.714285714285714, 12.714285714285714, 1.9264069264069263,\
            2.1795918367346938, 17.800000000000001, 20.342857142857142])

        self.in_flat_vector_to_weight = array([1, 2, 3, 4, 5, 6, 7, 8])
        self.in_flat_weighting_vector = array([1, 2, 3, 4, 5, 6, 7, 8])
        self.out_flat_weighted_vector = array([1, 2, 3, 4, 5, 6, 7, 8])

        self.in_second_flat_vector_to_weight = array([2, 3, 4, 5, 6])
        self.in_second_flat_weighting_vector = array([25, 30, 35, 40, 45])
        self.out_second_flat_weighted_vector = array([2, 3, 4, 5, 6])

        self.in_nd_array_vector_to_weight = array([[1, 2, 3],[2, 3, 4],\
            [5, 6, 7],[8, 9, 10]])
        self.in_nd_array_weighting_vector = array([1, 2, 3, 4])
        self.out_nd_array_flat_vector = array([[1, 2, 3],[2, 3, 4],\
            [5, 6, 7],[8, 9, 10]])


        test_weighted_output = weight_by_vector(self.in_vector_to_weight,\
            self.in_weighting_vector)
        self.assertEqual(test_weighted_output, self.out_weighted_vector)

        flat_test_weighted_output = weight_by_vector(\
            self.in_flat_vector_to_weight,self.in_flat_weighting_vector)
        self.assertEqual(flat_test_weighted_output, self.out_flat_weighted_vector)

        second_flat_test_weighted_output = weight_by_vector(\
            self.in_second_flat_vector_to_weight,self.in_second_flat_weighting_vector)
        self.assertEqual(second_flat_test_weighted_output, self.out_second_flat_weighted_vector)

    def test_windowed_diff(self):
        """Test correct functioning of the modified first difference """

        in_array_windowed_diff = array([24, 15, 28, 16, 28, 43, 12, 53])

        # check all the disallowed beahviours
        with self.assertRaises(ValueError):
            windowed_diff(in_array_windowed_diff, -10)
        with self.assertRaises(ValueError):
            windowed_diff(in_array_windowed_diff, 8)
        with self.assertRaises(ValueError):
            windowed_diff(in_array_windowed_diff, 50)

        # checks for correct behaviour with a 1-d vector
        exp_resutl = array([-4.3333333333333321, 9.0, 1.0, \
            11.666666666666668, 8.0, -3.6666666666666643, 41.0, 0.0])
        calc_result = windowed_diff(in_array_windowed_diff, 3)
        self.assertEqual(calc_result, exp_resutl)

        exp_resutl = [-9.0, 13.0, -12.0, 12.0, 15.0, -31.0,\
            41.0, 0.0]
        calc_result = windowed_diff(in_array_windowed_diff, 1)
        self.assertEqual(calc_result, exp_resutl)

        # checks for correct behaviour with an n-d vector
        in_nd_array_windowed_diff = array([array([2, 5, 1, 6]),\
            array([7, 1, 6, 3]), array([1, 8, 3, 5]), array([7, 3, 2, 6]),\
            array([8, 1, 6, 1]), array([15, 5, 4, 1]), array([1, 5, 1, 2]),\
            array([33, 5, 67, 12])])
        exp_result = [array([ 2. , -0.5,  3.5, -2. ]),\
            array([-3. ,  4.5, -3.5,  2.5]), array([ 6.5, -6. ,  1. , -1.5]),\
            array([ 4.5,  0. ,  3. , -5. ]), array([ 0. ,  4. , -3.5,  0.5]),\
            array([  2.,   0.,  30.,   6.]), array([ 32.,   0.,  66.,  10.]),\
            array([ 0.,  0.,  0.,  0.])]
        calc_result = windowed_diff(in_nd_array_windowed_diff, 2)
        self.assertEqual(calc_result, exp_result)

        return

exp_kin_full=\
['@kinemage {Day_unscaled}', '@dimension {PC1} {PC2} {PC3}', '@dimminmax -0.219044992 0.080504323 -0.212014503 0.079674486 -0.088353435 0.09233683', '@master {points}', '@master {labels}', '@hsvcolor {blue1} 240.0 100.0 100.0', '@hsvcolor {blue2} 211.0 42.0 85.0', '@hsvcolor {blue3} 197.0 100.0 100.0', '@hsvcolor {brown1} 36.0 89.0 42.0', '@hsvcolor {brown2} 33.0 45.0 77.0', '@hsvcolor {cyan1} 184.0 49.0 96.0', '@hsvcolor {gray1} 0.0 0.0 50.2', '@hsvcolor {gray2} 0.0 0.0 75.3', '@hsvcolor {green1} 120.0 100.0 50.2', '@hsvcolor {green2} 142.0 36.0 79.0', '@hsvcolor {green3} 60.0 100.0 50.2', '@hsvcolor {green4} 81.0 100.0 26.0', '@hsvcolor {lime} 123.0 99.0 96.0', '@hsvcolor {orange1} 28.0 98.0 95.0', '@hsvcolor {orange2} 32.0 46.0 99.0', '@hsvcolor {orange3} 26.0 100.0 65.0', '@hsvcolor {pink1} 333.0 37.0 96.0', '@hsvcolor {purple1} 302.0 73.0 57.0', '@hsvcolor {purple2} 269.0 29.0 75.0', '@hsvcolor {purple4} 264.0 75.0 100.0', '@hsvcolor {red1} 0.0 100.0 100.0', '@hsvcolor {red2} 14.0 51.0 97.0', '@hsvcolor {red3} 325.0 100.0 93.0', '@hsvcolor {red4} 348.0 31.0 74.0', '@hsvcolor {red5} 0.0 100.0 50.2', '@hsvcolor {teal1} 178.0 42.0 63.0', '@hsvcolor {teal3} 180.0 100.0 50.2', '@hsvcolor {yellow1} 60.0 100.0 100.0', '@hsvcolor {yellow2} 56.0 40.0 100.0', '@hsvcolor {white} 180.0 0.0 100.0', '@group {Day1 (n=3)} collapsible', '@balllist color=red1 radius=0.00299549315 alpha=0.75 dimension=3 master={points} nobutton', '{Sample1} -0.219044992 0.079674486 0.09233683\n{Sample2} -0.042258081 0.000204041 0.024837603\n{Sample3} 0.080504323 -0.212014503 -0.088353435', '@labellist color=red1 radius=0.00299549315 alpha=0.75 dimension=3 master={labels} nobutton', '{Sample1} -0.219044992 0.079674486 0.09233683\n{Sample2} -0.042258081 0.000204041 0.024837603\n{Sample3} 0.080504323 -0.212014503 -0.088353435', '@group {axes} collapsible', '@vectorlist {PC1 line} dimension=3 on', '-0.2299972416 -0.22261522815 -0.09277110675 white', '0.08452953915 -0.22261522815 -0.09277110675 white', '@labellist {PC1 (25%)} dimension=3 on', '{PC1 (25%)}0.0887560161075 -0.22261522815 -0.09277110675 white', '@vectorlist {PC2 line} dimension=3 on', '-0.2299972416 -0.22261522815 -0.09277110675 white', '-0.2299972416 0.0836582103 -0.09277110675 white', '@labellist {PC2 (30%)} dimension=3 on', '{PC2 (30%)}-0.2299972416 0.087841120815 -0.09277110675 white', '@vectorlist {PC3 line} dimension=3 on', '-0.2299972416 -0.22261522815 -0.09277110675 white', '-0.2299972416 -0.22261522815 0.0969536715 white', '@labellist {PC3 (35%)} dimension=3 on', '{PC3 (35%)}-0.2299972416 -0.22261522815 0.101801355075 white', '@kinemage {Day_scaled}', '@dimension {PC1} {PC2} {PC3}', '@dimminmax -0.156460708571 0.0575030878571 -0.181726716857 0.0682924165714 -0.088353435 0.09233683', '@master {points}', '@master {labels}', '@hsvcolor {blue1} 240.0 100.0 100.0', '@hsvcolor {blue2} 211.0 42.0 85.0', '@hsvcolor {blue3} 197.0 100.0 100.0', '@hsvcolor {brown1} 36.0 89.0 42.0', '@hsvcolor {brown2} 33.0 45.0 77.0', '@hsvcolor {cyan1} 184.0 49.0 96.0', '@hsvcolor {gray1} 0.0 0.0 50.2', '@hsvcolor {gray2} 0.0 0.0 75.3', '@hsvcolor {green1} 120.0 100.0 50.2', '@hsvcolor {green2} 142.0 36.0 79.0', '@hsvcolor {green3} 60.0 100.0 50.2', '@hsvcolor {green4} 81.0 100.0 26.0', '@hsvcolor {lime} 123.0 99.0 96.0', '@hsvcolor {orange1} 28.0 98.0 95.0', '@hsvcolor {orange2} 32.0 46.0 99.0', '@hsvcolor {orange3} 26.0 100.0 65.0', '@hsvcolor {pink1} 333.0 37.0 96.0', '@hsvcolor {purple1} 302.0 73.0 57.0', '@hsvcolor {purple2} 269.0 29.0 75.0', '@hsvcolor {purple4} 264.0 75.0 100.0', '@hsvcolor {red1} 0.0 100.0 100.0', '@hsvcolor {red2} 14.0 51.0 97.0', '@hsvcolor {red3} 325.0 100.0 93.0', '@hsvcolor {red4} 348.0 31.0 74.0', '@hsvcolor {red5} 0.0 100.0 50.2', '@hsvcolor {teal1} 178.0 42.0 63.0', '@hsvcolor {teal3} 180.0 100.0 50.2', '@hsvcolor {yellow1} 60.0 100.0 100.0', '@hsvcolor {yellow2} 56.0 40.0 100.0', '@hsvcolor {white} 180.0 0.0 100.0', '@group {Day1 (n=3)} collapsible', '@balllist color=red1 radius=0.00213963796429 alpha=0.75 dimension=3 master={points} nobutton', '{Sample1} -0.156460708571 0.0682924165714 0.09233683\n{Sample2} -0.0301843435714 0.000174892285714 0.024837603\n{Sample3} 0.0575030878571 -0.181726716857 -0.088353435', '@labellist color=red1 radius=0.00213963796429 alpha=0.75 dimension=3 master={labels} nobutton', '{Sample1} -0.156460708571 0.0682924165714 0.09233683\n{Sample2} -0.0301843435714 0.000174892285714 0.024837603\n{Sample3} 0.0575030878571 -0.181726716857 -0.088353435', '@group {axes} collapsible', '@vectorlist {PC1 line} dimension=3 on', '-0.164283744 -0.1908130527 -0.09277110675 white', '0.06037824225 -0.1908130527 -0.09277110675 white', '@labellist {PC1 (25%)} dimension=3 on', '{PC1 (25%)}0.0633971543625 -0.1908130527 -0.09277110675 white', '@vectorlist {PC2 line} dimension=3 on', '-0.164283744 -0.1908130527 -0.09277110675 white', '-0.164283744 0.0717070374 -0.09277110675 white', '@labellist {PC2 (30%)} dimension=3 on', '{PC2 (30%)}-0.164283744 0.07529238927 -0.09277110675 white', '@vectorlist {PC3 line} dimension=3 on', '-0.164283744 -0.1908130527 -0.09277110675 white', '-0.164283744 -0.1908130527 0.0969536715 white', '@labellist {PC3 (35%)} dimension=3 on', '{PC3 (35%)}-0.164283744 -0.1908130527 0.101801355075 white']

exp_kin_full_axes =\
['@kinemage {Day_unscaled}', '@dimension {Height} {Weight} {PC1} {PC2} {PC3}', '@dimminmax -0.219044992 0.161008646 -0.219044992 0.161008646 -0.219044992 0.080504323 -0.212014503 0.079674486 -0.088353435 0.09233683', '@master {points}', '@master {labels}', '@hsvcolor {blue1} 240.0 100.0 100.0', '@hsvcolor {blue2} 211.0 42.0 85.0', '@hsvcolor {blue3} 197.0 100.0 100.0', '@hsvcolor {brown1} 36.0 89.0 42.0', '@hsvcolor {brown2} 33.0 45.0 77.0', '@hsvcolor {cyan1} 184.0 49.0 96.0', '@hsvcolor {gray1} 0.0 0.0 50.2', '@hsvcolor {gray2} 0.0 0.0 75.3', '@hsvcolor {green1} 120.0 100.0 50.2', '@hsvcolor {green2} 142.0 36.0 79.0', '@hsvcolor {green3} 60.0 100.0 50.2', '@hsvcolor {green4} 81.0 100.0 26.0', '@hsvcolor {lime} 123.0 99.0 96.0', '@hsvcolor {orange1} 28.0 98.0 95.0', '@hsvcolor {orange2} 32.0 46.0 99.0', '@hsvcolor {orange3} 26.0 100.0 65.0', '@hsvcolor {pink1} 333.0 37.0 96.0', '@hsvcolor {purple1} 302.0 73.0 57.0', '@hsvcolor {purple2} 269.0 29.0 75.0', '@hsvcolor {purple4} 264.0 75.0 100.0', '@hsvcolor {red1} 0.0 100.0 100.0', '@hsvcolor {red2} 14.0 51.0 97.0', '@hsvcolor {red3} 325.0 100.0 93.0', '@hsvcolor {red4} 348.0 31.0 74.0', '@hsvcolor {red5} 0.0 100.0 50.2', '@hsvcolor {teal1} 178.0 42.0 63.0', '@hsvcolor {teal3} 180.0 100.0 50.2', '@hsvcolor {yellow1} 60.0 100.0 100.0', '@hsvcolor {yellow2} 56.0 40.0 100.0', '@hsvcolor {white} 180.0 0.0 100.0', '@group {Day1 (n=3)} collapsible', '@balllist color=red1 radius=0.00380053638 alpha=0.75 dimension=5 master={points} nobutton', '{Sample1} -0.219044992 0.161008646 -0.219044992 0.079674486 0.09233683\n{Sample2} -0.029018173 -0.029018173 -0.042258081 0.000204041 0.024837603\n{Sample3} 0.161008646 -0.219044992 0.080504323 -0.212014503 -0.088353435', '@labellist color=red1 radius=0.00380053638 alpha=0.75 dimension=5 master={labels} nobutton', '{Sample1} -0.219044992 0.161008646 -0.219044992 0.079674486 0.09233683\n{Sample2} -0.029018173 -0.029018173 -0.042258081 0.000204041 0.024837603\n{Sample3} 0.161008646 -0.219044992 0.080504323 -0.212014503 -0.088353435', '@group {axes} collapsible', '@vectorlist {Height line} dimension=5 on', '-0.2299972416 -0.2299972416 -0.2299972416 -0.22261522815 -0.09277110675 white', '0.1690590783 -0.2299972416 -0.2299972416 -0.22261522815 -0.09277110675 white', '@labellist {Height} dimension=5 on', '{Height}0.177512032215 -0.2299972416 -0.2299972416 -0.22261522815 -0.09277110675 white', '@vectorlist {Weight line} dimension=5 on', '-0.2299972416 -0.2299972416 -0.2299972416 -0.22261522815 -0.09277110675 white', '-0.2299972416 0.1690590783 -0.2299972416 -0.22261522815 -0.09277110675 white', '@labellist {Weight} dimension=5 on', '{Weight}-0.2299972416 0.177512032215 -0.2299972416 -0.22261522815 -0.09277110675 white', '@vectorlist {PC1 line} dimension=5 on', '-0.2299972416 -0.2299972416 -0.2299972416 -0.22261522815 -0.09277110675 white', '-0.2299972416 -0.2299972416 0.08452953915 -0.22261522815 -0.09277110675 white', '@labellist {PC1 (25%)} dimension=5 on', '{PC1 (25%)}-0.2299972416 -0.2299972416 0.0887560161075 -0.22261522815 -0.09277110675 white', '@vectorlist {PC2 line} dimension=5 off', '-0.2299972416 -0.2299972416 -0.2299972416 -0.22261522815 -0.09277110675 white', '-0.2299972416 -0.2299972416 -0.2299972416 0.0836582103 -0.09277110675 white', '@labellist {PC2 (30%)} dimension=5 off', '{PC2 (30%)}-0.2299972416 -0.2299972416 -0.2299972416 0.087841120815 -0.09277110675 white', '@vectorlist {PC3 line} dimension=5 off', '-0.2299972416 -0.2299972416 -0.2299972416 -0.22261522815 -0.09277110675 white', '-0.2299972416 -0.2299972416 -0.2299972416 -0.22261522815 0.0969536715 white', '@labellist {PC3 (35%)} dimension=5 off', '{PC3 (35%)}-0.2299972416 -0.2299972416 -0.2299972416 -0.22261522815 0.101801355075 white', '@kinemage {Day_scaled}', '@dimension {Height} {Weight} {PC1} {PC2} {PC3}', '@dimminmax -0.156460708571 0.115006175714 -0.156460708571 0.115006175714 -0.156460708571 0.0575030878571 -0.181726716857 0.0682924165714 -0.088353435 0.09233683', '@master {points}', '@master {labels}', '@hsvcolor {blue1} 240.0 100.0 100.0', '@hsvcolor {blue2} 211.0 42.0 85.0', '@hsvcolor {blue3} 197.0 100.0 100.0', '@hsvcolor {brown1} 36.0 89.0 42.0', '@hsvcolor {brown2} 33.0 45.0 77.0', '@hsvcolor {cyan1} 184.0 49.0 96.0', '@hsvcolor {gray1} 0.0 0.0 50.2', '@hsvcolor {gray2} 0.0 0.0 75.3', '@hsvcolor {green1} 120.0 100.0 50.2', '@hsvcolor {green2} 142.0 36.0 79.0', '@hsvcolor {green3} 60.0 100.0 50.2', '@hsvcolor {green4} 81.0 100.0 26.0', '@hsvcolor {lime} 123.0 99.0 96.0', '@hsvcolor {orange1} 28.0 98.0 95.0', '@hsvcolor {orange2} 32.0 46.0 99.0', '@hsvcolor {orange3} 26.0 100.0 65.0', '@hsvcolor {pink1} 333.0 37.0 96.0', '@hsvcolor {purple1} 302.0 73.0 57.0', '@hsvcolor {purple2} 269.0 29.0 75.0', '@hsvcolor {purple4} 264.0 75.0 100.0', '@hsvcolor {red1} 0.0 100.0 100.0', '@hsvcolor {red2} 14.0 51.0 97.0', '@hsvcolor {red3} 325.0 100.0 93.0', '@hsvcolor {red4} 348.0 31.0 74.0', '@hsvcolor {red5} 0.0 100.0 50.2', '@hsvcolor {teal1} 178.0 42.0 63.0', '@hsvcolor {teal3} 180.0 100.0 50.2', '@hsvcolor {yellow1} 60.0 100.0 100.0', '@hsvcolor {yellow2} 56.0 40.0 100.0', '@hsvcolor {white} 180.0 0.0 100.0', '@group {Day1 (n=3)} collapsible', '@balllist color=red1 radius=0.00271466884286 alpha=0.75 dimension=5 master={points} nobutton', '{Sample1} -0.156460708571 0.115006175714 -0.156460708571 0.0682924165714 0.09233683\n{Sample2} -0.0207272664286 -0.0207272664286 -0.0301843435714 0.000174892285714 0.024837603\n{Sample3} 0.115006175714 -0.156460708571 0.0575030878571 -0.181726716857 -0.088353435', '@labellist color=red1 radius=0.00271466884286 alpha=0.75 dimension=5 master={labels} nobutton', '{Sample1} -0.156460708571 0.115006175714 -0.156460708571 0.0682924165714 0.09233683\n{Sample2} -0.0207272664286 -0.0207272664286 -0.0301843435714 0.000174892285714 0.024837603\n{Sample3} 0.115006175714 -0.156460708571 0.0575030878571 -0.181726716857 -0.088353435', '@group {axes} collapsible', '@vectorlist {Height line} dimension=5 on', '-0.164283744 -0.164283744 -0.164283744 -0.1908130527 -0.09277110675 white', '0.1207564845 -0.164283744 -0.164283744 -0.1908130527 -0.09277110675 white', '@labellist {Height} dimension=5 on', '{Height}0.126794308725 -0.164283744 -0.164283744 -0.1908130527 -0.09277110675 white', '@vectorlist {Weight line} dimension=5 on', '-0.164283744 -0.164283744 -0.164283744 -0.1908130527 -0.09277110675 white', '-0.164283744 0.1207564845 -0.164283744 -0.1908130527 -0.09277110675 white', '@labellist {Weight} dimension=5 on', '{Weight}-0.164283744 0.126794308725 -0.164283744 -0.1908130527 -0.09277110675 white', '@vectorlist {PC1 line} dimension=5 on', '-0.164283744 -0.164283744 -0.164283744 -0.1908130527 -0.09277110675 white', '-0.164283744 -0.164283744 0.06037824225 -0.1908130527 -0.09277110675 white', '@labellist {PC1 (25%)} dimension=5 on', '{PC1 (25%)}-0.164283744 -0.164283744 0.0633971543625 -0.1908130527 -0.09277110675 white', '@vectorlist {PC2 line} dimension=5 off', '-0.164283744 -0.164283744 -0.164283744 -0.1908130527 -0.09277110675 white', '-0.164283744 -0.164283744 -0.164283744 0.0717070374 -0.09277110675 white', '@labellist {PC2 (30%)} dimension=5 off', '{PC2 (30%)}-0.164283744 -0.164283744 -0.164283744 0.07529238927 -0.09277110675 white', '@vectorlist {PC3 line} dimension=5 off', '-0.164283744 -0.164283744 -0.164283744 -0.1908130527 -0.09277110675 white', '-0.164283744 -0.164283744 -0.164283744 -0.1908130527 0.0969536715 white', '@labellist {PC3 (35%)} dimension=5 off', '{PC3 (35%)}-0.164283744 -0.164283744 -0.164283744 -0.1908130527 0.101801355075 white']

exp_kin_vectors=\
['@kinemage {Day_unscaled}', '@dimension {Height} {PC1} {PC2} {PC3}', '@dimminmax 0.0 3.0 -0.219044992 0.080504323 -0.212014503 0.079674486 -160029789.0 0.09233683', '@master {points}', '@master {labels}', '@hsvcolor {blue1} 240.0 100.0 100.0', '@hsvcolor {blue2} 211.0 42.0 85.0', '@hsvcolor {blue3} 197.0 100.0 100.0', '@hsvcolor {brown1} 36.0 89.0 42.0', '@hsvcolor {brown2} 33.0 45.0 77.0', '@hsvcolor {cyan1} 184.0 49.0 96.0', '@hsvcolor {gray1} 0.0 0.0 50.2', '@hsvcolor {gray2} 0.0 0.0 75.3', '@hsvcolor {green1} 120.0 100.0 50.2', '@hsvcolor {green2} 142.0 36.0 79.0', '@hsvcolor {green3} 60.0 100.0 50.2', '@hsvcolor {green4} 81.0 100.0 26.0', '@hsvcolor {lime} 123.0 99.0 96.0', '@hsvcolor {orange1} 28.0 98.0 95.0', '@hsvcolor {orange2} 32.0 46.0 99.0', '@hsvcolor {orange3} 26.0 100.0 65.0', '@hsvcolor {pink1} 333.0 37.0 96.0', '@hsvcolor {purple1} 302.0 73.0 57.0', '@hsvcolor {purple2} 269.0 29.0 75.0', '@hsvcolor {purple4} 264.0 75.0 100.0', '@hsvcolor {red1} 0.0 100.0 100.0', '@hsvcolor {red2} 14.0 51.0 97.0', '@hsvcolor {red3} 325.0 100.0 93.0', '@hsvcolor {red4} 348.0 31.0 74.0', '@hsvcolor {red5} 0.0 100.0 50.2', '@hsvcolor {teal1} 178.0 42.0 63.0', '@hsvcolor {teal3} 180.0 100.0 50.2', '@hsvcolor {yellow1} 60.0 100.0 100.0', '@hsvcolor {yellow2} 56.0 40.0 100.0', '@hsvcolor {white} 180.0 0.0 100.0', '@group {Day1 (n=3)} collapsible', '@balllist color=red1 radius=0.03 alpha=0.75 dimension=4 master={points} nobutton', '{Sample1} 0.0 -0.219044992 0.079674486 0.09233683\n{Sample2} 1.0 -0.042258081 0.000204041 0.024837603\n{Sample3} 2.0 0.080504323 -0.212014503 -0.088353435', '@labellist color=red1 radius=0.03 alpha=0.75 dimension=4 master={labels} nobutton', '{Sample1} 0.0 -0.219044992 0.079674486 0.09233683\n{Sample2} 1.0 -0.042258081 0.000204041 0.024837603\n{Sample3} 2.0 0.080504323 -0.212014503 -0.088353435', '@vectorlist {trace} dimension=4 on', '@vectorlist {average} dimension=4 off', '0.0 -0.219044992 0.079674486 0.09233683 red1', '0.5 -0.1306515365 0.0399392635 0.0585872165 red1 P', '0.5 -0.1306515365 0.0399392635 0.0585872165 red1', '1.0 -0.042258081 0.000204041 0.024837603 red1 P', '1.0 -0.042258081 0.000204041 0.024837603 red1', '1.5 0.019123121 -0.105905231 -0.031757916 red1 P', '1.5 0.019123121 -0.105905231 -0.031757916 red1', '2.0 0.080504323 -0.212014503 -0.088353435 red1 P', '@group {axes} collapsible', '@vectorlist {Height line} dimension=4 on', '0.0 -0.2299972416 -0.22261522815 -168031278.45 white', '3.15 -0.2299972416 -0.22261522815 -168031278.45 white', '@labellist {Height} dimension=4 on', '{Height}3.3075 -0.2299972416 -0.22261522815 -168031278.45 white', '@vectorlist {PC1 line} dimension=4 on', '0.0 -0.2299972416 -0.22261522815 -168031278.45 white', '0.0 0.08452953915 -0.22261522815 -168031278.45 white', '@labellist {PC1 (25%)} dimension=4 on', '{PC1 (25%)}0.0 0.0887560161075 -0.22261522815 -168031278.45 white', '@vectorlist {PC2 line} dimension=4 on', '0.0 -0.2299972416 -0.22261522815 -168031278.45 white', '0.0 -0.2299972416 0.0836582103 -168031278.45 white', '@labellist {PC2 (30%)} dimension=4 on', '{PC2 (30%)}0.0 -0.2299972416 0.087841120815 -168031278.45 white', '@vectorlist {PC3 line} dimension=4 off', '0.0 -0.2299972416 -0.22261522815 -168031278.45 white', '0.0 -0.2299972416 -0.22261522815 0.0969536715 white', '@labellist {PC3 (35%)} dimension=4 off', '{PC3 (35%)}0.0 -0.2299972416 -0.22261522815 0.101801355075 white']

exp_kin_partial=\
['@kinemage {_unscaled}', '@dimension {PC1} {PC2} {PC3}', '@dimminmax -0.219044992 0.080504323 -0.212014503 0.079674486 -0.088353435 0.09233683', '@master {points}', '@master {labels}', '@hsvcolor {blue1} 240.0 100.0 100.0', '@hsvcolor {blue2} 211.0 42.0 85.0', '@hsvcolor {blue3} 197.0 100.0 100.0', '@hsvcolor {brown1} 36.0 89.0 42.0', '@hsvcolor {brown2} 33.0 45.0 77.0', '@hsvcolor {cyan1} 184.0 49.0 96.0', '@hsvcolor {gray1} 0.0 0.0 50.2', '@hsvcolor {gray2} 0.0 0.0 75.3', '@hsvcolor {green1} 120.0 100.0 50.2', '@hsvcolor {green2} 142.0 36.0 79.0', '@hsvcolor {green3} 60.0 100.0 50.2', '@hsvcolor {green4} 81.0 100.0 26.0', '@hsvcolor {lime} 123.0 99.0 96.0', '@hsvcolor {orange1} 28.0 98.0 95.0', '@hsvcolor {orange2} 32.0 46.0 99.0', '@hsvcolor {orange3} 26.0 100.0 65.0', '@hsvcolor {pink1} 333.0 37.0 96.0', '@hsvcolor {purple1} 302.0 73.0 57.0', '@hsvcolor {purple2} 269.0 29.0 75.0', '@hsvcolor {purple4} 264.0 75.0 100.0', '@hsvcolor {red1} 0.0 100.0 100.0', '@hsvcolor {red2} 14.0 51.0 97.0', '@hsvcolor {red3} 325.0 100.0 93.0', '@hsvcolor {red4} 348.0 31.0 74.0', '@hsvcolor {red5} 0.0 100.0 50.2', '@hsvcolor {teal1} 178.0 42.0 63.0', '@hsvcolor {teal3} 180.0 100.0 50.2', '@hsvcolor {yellow1} 60.0 100.0 100.0', '@hsvcolor {yellow2} 56.0 40.0 100.0', '@hsvcolor {white} 180.0 0.0 100.0', '@group {Day1 (n=3)} collapsible', '@balllist color=blue1 radius=0.00299549315 alpha=0.75 dimension=3 master={points} nobutton', '{Sample1} -0.219044992 0.079674486 0.09233683\n{Sample2} -0.042258081 0.000204041 0.024837603\n{Sample3} 0.080504323 -0.212014503 -0.088353435', '@labellist color=blue1 radius=0.00299549315 alpha=0.75 dimension=3 master={labels} nobutton', '{Sample1} -0.219044992 0.079674486 0.09233683\n{Sample2} -0.042258081 0.000204041 0.024837603\n{Sample3} 0.080504323 -0.212014503 -0.088353435', '@group {axes} collapsible', '@vectorlist {PC1 line} dimension=3 on', '-0.2299972416 -0.22261522815 -0.09277110675 white', '0.08452953915 -0.22261522815 -0.09277110675 white', '@labellist {PC1 (25%)} dimension=3 on', '{PC1 (25%)}0.0887560161075 -0.22261522815 -0.09277110675 white', '@vectorlist {PC2 line} dimension=3 on', '-0.2299972416 -0.22261522815 -0.09277110675 white', '-0.2299972416 0.0836582103 -0.09277110675 white', '@labellist {PC2 (30%)} dimension=3 on', '{PC2 (30%)}-0.2299972416 0.087841120815 -0.09277110675 white', '@vectorlist {PC3 line} dimension=3 on', '-0.2299972416 -0.22261522815 -0.09277110675 white', '-0.2299972416 -0.22261522815 0.0969536715 white', '@labellist {PC3 (35%)} dimension=3 on', '{PC3 (35%)}-0.2299972416 -0.22261522815 0.101801355075 white']


exp_kin_partial_axes=\
['@kinemage {_unscaled}', '@dimension {Height} {Weight} {PC1} {PC2} {PC3}', '@dimminmax -0.219044992 0.161008646 -0.219044992 0.161008646 -0.219044992 0.080504323 -0.212014503 0.079674486 -0.088353435 0.09233683', '@master {points}', '@master {labels}', '@hsvcolor {blue1} 240.0 100.0 100.0', '@hsvcolor {blue2} 211.0 42.0 85.0', '@hsvcolor {blue3} 197.0 100.0 100.0', '@hsvcolor {brown1} 36.0 89.0 42.0', '@hsvcolor {brown2} 33.0 45.0 77.0', '@hsvcolor {cyan1} 184.0 49.0 96.0', '@hsvcolor {gray1} 0.0 0.0 50.2', '@hsvcolor {gray2} 0.0 0.0 75.3', '@hsvcolor {green1} 120.0 100.0 50.2', '@hsvcolor {green2} 142.0 36.0 79.0', '@hsvcolor {green3} 60.0 100.0 50.2', '@hsvcolor {green4} 81.0 100.0 26.0', '@hsvcolor {lime} 123.0 99.0 96.0', '@hsvcolor {orange1} 28.0 98.0 95.0', '@hsvcolor {orange2} 32.0 46.0 99.0', '@hsvcolor {orange3} 26.0 100.0 65.0', '@hsvcolor {pink1} 333.0 37.0 96.0', '@hsvcolor {purple1} 302.0 73.0 57.0', '@hsvcolor {purple2} 269.0 29.0 75.0', '@hsvcolor {purple4} 264.0 75.0 100.0', '@hsvcolor {red1} 0.0 100.0 100.0', '@hsvcolor {red2} 14.0 51.0 97.0', '@hsvcolor {red3} 325.0 100.0 93.0', '@hsvcolor {red4} 348.0 31.0 74.0', '@hsvcolor {red5} 0.0 100.0 50.2', '@hsvcolor {teal1} 178.0 42.0 63.0', '@hsvcolor {teal3} 180.0 100.0 50.2', '@hsvcolor {yellow1} 60.0 100.0 100.0', '@hsvcolor {yellow2} 56.0 40.0 100.0', '@hsvcolor {white} 180.0 0.0 100.0', '@group {Day1 (n=3)} collapsible', '@balllist color=blue1 radius=0.00380053638 alpha=0.75 dimension=5 master={points} nobutton', '{Sample1} -0.219044992 0.161008646 -0.219044992 0.079674486 0.09233683\n{Sample2} -0.029018173 -0.029018173 -0.042258081 0.000204041 0.024837603\n{Sample3} 0.161008646 -0.219044992 0.080504323 -0.212014503 -0.088353435', '@labellist color=blue1 radius=0.00380053638 alpha=0.75 dimension=5 master={labels} nobutton', '{Sample1} -0.219044992 0.161008646 -0.219044992 0.079674486 0.09233683\n{Sample2} -0.029018173 -0.029018173 -0.042258081 0.000204041 0.024837603\n{Sample3} 0.161008646 -0.219044992 0.080504323 -0.212014503 -0.088353435', '@group {axes} collapsible', '@vectorlist {Height line} dimension=5 on', '-0.2299972416 -0.2299972416 -0.2299972416 -0.22261522815 -0.09277110675 white', '0.1690590783 -0.2299972416 -0.2299972416 -0.22261522815 -0.09277110675 white', '@labellist {Height} dimension=5 on', '{Height}0.177512032215 -0.2299972416 -0.2299972416 -0.22261522815 -0.09277110675 white', '@vectorlist {Weight line} dimension=5 on', '-0.2299972416 -0.2299972416 -0.2299972416 -0.22261522815 -0.09277110675 white', '-0.2299972416 0.1690590783 -0.2299972416 -0.22261522815 -0.09277110675 white', '@labellist {Weight} dimension=5 on', '{Weight}-0.2299972416 0.177512032215 -0.2299972416 -0.22261522815 -0.09277110675 white', '@vectorlist {PC1 line} dimension=5 on', '-0.2299972416 -0.2299972416 -0.2299972416 -0.22261522815 -0.09277110675 white', '-0.2299972416 -0.2299972416 0.08452953915 -0.22261522815 -0.09277110675 white', '@labellist {PC1 (25%)} dimension=5 on', '{PC1 (25%)}-0.2299972416 -0.2299972416 0.0887560161075 -0.22261522815 -0.09277110675 white', '@vectorlist {PC2 line} dimension=5 off', '-0.2299972416 -0.2299972416 -0.2299972416 -0.22261522815 -0.09277110675 white', '-0.2299972416 -0.2299972416 -0.2299972416 0.0836582103 -0.09277110675 white', '@labellist {PC2 (30%)} dimension=5 off', '{PC2 (30%)}-0.2299972416 -0.2299972416 -0.2299972416 0.087841120815 -0.09277110675 white', '@vectorlist {PC3 line} dimension=5 off', '-0.2299972416 -0.2299972416 -0.2299972416 -0.22261522815 -0.09277110675 white', '-0.2299972416 -0.2299972416 -0.2299972416 -0.22261522815 0.0969536715 white', '@labellist {PC3 (35%)} dimension=5 off', '{PC3 (35%)}-0.2299972416 -0.2299972416 -0.2299972416 -0.22261522815 0.101801355075 white']
#expected ellipsoid faces with no translation/scaling
exp_make_ellipsoid_faces = \
[[(0.85065000000000002, 0.52573000000000003, 0.0), (0.0, 0.85065000000000002, 0.52573000000000003), (0.52573000000000003, 0.0, 0.85065000000000002)], [(-0.85065000000000002, 0.52573000000000003, 0.0), (0.0, 0.85065000000000002, -0.52573000000000003), (-0.52573000000000003, 0.0, -0.85065000000000002)], [(0.85065000000000002, -0.52573000000000003, 0.0), (0.0, -0.85065000000000002, 0.52573000000000003), (0.0, -0.85065000000000002, -0.52573000000000003)], [(-0.52573000000000003, 0.0, -0.85065000000000002), (-0.85065000000000002, -0.52573000000000003, 0.0), (-0.85065000000000002, 0.52573000000000003, 0.0)], [(0.85065000000000002, 0.52573000000000003, 0.0), (0.52573000000000003, 0.0, -0.85065000000000002), (0.0, 0.85065000000000002, -0.52573000000000003)], [(-0.85065000000000002, -0.52573000000000003, 0.0), (0.0, -0.85065000000000002, 0.52573000000000003), (-0.52573000000000003, 0.0, 0.85065000000000002)], [(-0.85065000000000002, -0.52573000000000003, 0.0), (0.0, -0.85065000000000002, -0.52573000000000003), (0.0, -0.85065000000000002, 0.52573000000000003)], [(0.0, 0.85065000000000002, 0.52573000000000003), (-0.52573000000000003, 0.0, 0.85065000000000002), (0.52573000000000003, 0.0, 0.85065000000000002)], [(0.85065000000000002, -0.52573000000000003, 0.0), (0.52573000000000003, 0.0, 0.85065000000000002), (0.0, -0.85065000000000002, 0.52573000000000003)], [(-0.85065000000000002, -0.52573000000000003, 0.0), (-0.52573000000000003, 0.0, -0.85065000000000002), (0.0, -0.85065000000000002, -0.52573000000000003)], [(0.52573000000000003, 0.0, 0.85065000000000002), (0.85065000000000002, -0.52573000000000003, 0.0), (0.85065000000000002, 0.52573000000000003, 0.0)], [(0.0, -0.85065000000000002, 0.52573000000000003), (0.52573000000000003, 0.0, 0.85065000000000002), (-0.52573000000000003, 0.0, 0.85065000000000002)], [(0.85065000000000002, -0.52573000000000003, 0.0), (0.0, -0.85065000000000002, -0.52573000000000003), (0.52573000000000003, 0.0, -0.85065000000000002)], [(0.85065000000000002, 0.52573000000000003, 0.0), (0.0, 0.85065000000000002, -0.52573000000000003), (0.0, 0.85065000000000002, 0.52573000000000003)], [(0.52573000000000003, 0.0, -0.85065000000000002), (0.85065000000000002, 0.52573000000000003, 0.0), (0.85065000000000002, -0.52573000000000003, 0.0)], [(0.0, 0.85065000000000002, -0.52573000000000003), (0.52573000000000003, 0.0, -0.85065000000000002), (-0.52573000000000003, 0.0, -0.85065000000000002)], [(-0.85065000000000002, 0.52573000000000003, 0.0), (-0.52573000000000003, 0.0, 0.85065000000000002), (0.0, 0.85065000000000002, 0.52573000000000003)], [(-0.85065000000000002, 0.52573000000000003, 0.0), (0.0, 0.85065000000000002, 0.52573000000000003), (0.0, 0.85065000000000002, -0.52573000000000003)], [(-0.52573000000000003, 0.0, 0.85065000000000002), (-0.85065000000000002, 0.52573000000000003, 0.0), (-0.85065000000000002, -0.52573000000000003, 0.0)], [(0.0, -0.85065000000000002, -0.52573000000000003), (-0.52573000000000003, 0.0, -0.85065000000000002), (0.52573000000000003, 0.0, -0.85065000000000002)]]

#expected ellipsoid faces with translation by (-1,2,3), scaling by (.2,2,20)
exp_make_ellipsoid_faces_transformed = \
[[(-0.82986983832959194, 3.051462224238267, 3.0), (-1.0, 3.7013016167040798, 13.514622242382671), (-0.89485377757617324, 2.0, 20.013016167040799)], [(-1.1701301616704081, 3.051462224238267, 3.0), (-1.0, 3.7013016167040798, -7.5146222423826714), (-1.1051462224238267, 2.0, -14.013016167040799)], [(-0.82986983832959194, 0.94853777576173282, 3.0), (-1.0, 0.29869838329592002, 13.514622242382671), (-1.0, 0.29869838329592002, -7.5146222423826714)], [(-1.1051462224238267, 2.0, -14.013016167040799), (-1.1701301616704081, 0.94853777576173282, 3.0), (-1.1701301616704081, 3.051462224238267, 3.0)], [(-0.82986983832959194, 3.051462224238267, 3.0), (-0.89485377757617324, 2.0, -14.013016167040799), (-1.0, 3.7013016167040798, -7.5146222423826714)], [(-1.1701301616704081, 0.94853777576173282, 3.0), (-1.0, 0.29869838329592002, 13.514622242382671), (-1.1051462224238267, 2.0, 20.013016167040799)], [(-1.1701301616704081, 0.94853777576173282, 3.0), (-1.0, 0.29869838329592002, -7.5146222423826714), (-1.0, 0.29869838329592002, 13.514622242382671)], [(-1.0, 3.7013016167040798, 13.514622242382671), (-1.1051462224238267, 2.0, 20.013016167040799), (-0.89485377757617324, 2.0, 20.013016167040799)], [(-0.82986983832959194, 0.94853777576173282, 3.0), (-0.89485377757617324, 2.0, 20.013016167040799), (-1.0, 0.29869838329592002, 13.514622242382671)], [(-1.1701301616704081, 0.94853777576173282, 3.0), (-1.1051462224238267, 2.0, -14.013016167040799), (-1.0, 0.29869838329592002, -7.5146222423826714)], [(-0.89485377757617324, 2.0, 20.013016167040799), (-0.82986983832959194, 0.94853777576173282, 3.0), (-0.82986983832959194, 3.051462224238267, 3.0)], [(-1.0, 0.29869838329592002, 13.514622242382671), (-0.89485377757617324, 2.0, 20.013016167040799), (-1.1051462224238267, 2.0, 20.013016167040799)], [(-0.82986983832959194, 0.94853777576173282, 3.0), (-1.0, 0.29869838329592002, -7.5146222423826714), (-0.89485377757617324, 2.0, -14.013016167040799)], [(-0.82986983832959194, 3.051462224238267, 3.0), (-1.0, 3.7013016167040798, -7.5146222423826714), (-1.0, 3.7013016167040798, 13.514622242382671)], [(-0.89485377757617324, 2.0, -14.013016167040799), (-0.82986983832959194, 3.051462224238267, 3.0), (-0.82986983832959194, 0.94853777576173282, 3.0)], [(-1.0, 3.7013016167040798, -7.5146222423826714), (-0.89485377757617324, 2.0, -14.013016167040799), (-1.1051462224238267, 2.0, -14.013016167040799)], [(-1.1701301616704081, 3.051462224238267, 3.0), (-1.1051462224238267, 2.0, 20.013016167040799), (-1.0, 3.7013016167040798, 13.514622242382671)], [(-1.1701301616704081, 3.051462224238267, 3.0), (-1.0, 3.7013016167040798, 13.514622242382671), (-1.0, 3.7013016167040798, -7.5146222423826714)], [(-1.1051462224238267, 2.0, 20.013016167040799), (-1.1701301616704081, 3.051462224238267, 3.0), (-1.1701301616704081, 0.94853777576173282, 3.0)], [(-1.0, 0.29869838329592002, -7.5146222423826714), (-1.1051462224238267, 2.0, -14.013016167040799), (-0.89485377757617324, 2.0, -14.013016167040799)]]

exp_make_mage_ellipsoids = \
['@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '0.850650808352 0.525731112119 0.0', '0.0 0.850650808352 0.525731112119', '0.525731112119 0.0 0.850650808352', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-0.850650808352 0.525731112119 0.0', '0.0 0.850650808352 -0.525731112119', '-0.525731112119 0.0 -0.850650808352', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '0.850650808352 -0.525731112119 0.0', '0.0 -0.850650808352 0.525731112119', '0.0 -0.850650808352 -0.525731112119', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-0.525731112119 0.0 -0.850650808352', '-0.850650808352 -0.525731112119 0.0', '-0.850650808352 0.525731112119 0.0', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '0.850650808352 0.525731112119 0.0', '0.525731112119 0.0 -0.850650808352', '0.0 0.850650808352 -0.525731112119', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-0.850650808352 -0.525731112119 0.0', '0.0 -0.850650808352 0.525731112119', '-0.525731112119 0.0 0.850650808352', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-0.850650808352 -0.525731112119 0.0', '0.0 -0.850650808352 -0.525731112119', '0.0 -0.850650808352 0.525731112119', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '0.0 0.850650808352 0.525731112119', '-0.525731112119 0.0 0.850650808352', '0.525731112119 0.0 0.850650808352', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '0.850650808352 -0.525731112119 0.0', '0.525731112119 0.0 0.850650808352', '0.0 -0.850650808352 0.525731112119', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-0.850650808352 -0.525731112119 0.0', '-0.525731112119 0.0 -0.850650808352', '0.0 -0.850650808352 -0.525731112119', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '0.525731112119 0.0 0.850650808352', '0.850650808352 -0.525731112119 0.0', '0.850650808352 0.525731112119 0.0', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '0.0 -0.850650808352 0.525731112119', '0.525731112119 0.0 0.850650808352', '-0.525731112119 0.0 0.850650808352', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '0.850650808352 -0.525731112119 0.0', '0.0 -0.850650808352 -0.525731112119', '0.525731112119 0.0 -0.850650808352', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '0.850650808352 0.525731112119 0.0', '0.0 0.850650808352 -0.525731112119', '0.0 0.850650808352 0.525731112119', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '0.525731112119 0.0 -0.850650808352', '0.850650808352 0.525731112119 0.0', '0.850650808352 -0.525731112119 0.0', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '0.0 0.850650808352 -0.525731112119', '0.525731112119 0.0 -0.850650808352', '-0.525731112119 0.0 -0.850650808352', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-0.850650808352 0.525731112119 0.0', '-0.525731112119 0.0 0.850650808352', '0.0 0.850650808352 0.525731112119', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-0.850650808352 0.525731112119 0.0', '0.0 0.850650808352 0.525731112119', '0.0 0.850650808352 -0.525731112119', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-0.525731112119 0.0 0.850650808352', '-0.850650808352 0.525731112119 0.0', '-0.850650808352 -0.525731112119 0.0', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '0.0 -0.850650808352 -0.525731112119', '-0.525731112119 0.0 -0.850650808352', '0.525731112119 0.0 -0.850650808352', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-0.82986983833 3.05146222424 3.0', '-1.0 3.7013016167 13.5146222424', '-0.894853777576 2.0 20.013016167', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-1.17013016167 3.05146222424 3.0', '-1.0 3.7013016167 -7.51462224238', '-1.10514622242 2.0 -14.013016167', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-0.82986983833 0.948537775762 3.0', '-1.0 0.298698383296 13.5146222424', '-1.0 0.298698383296 -7.51462224238', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-1.10514622242 2.0 -14.013016167', '-1.17013016167 0.948537775762 3.0', '-1.17013016167 3.05146222424 3.0', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-0.82986983833 3.05146222424 3.0', '-0.894853777576 2.0 -14.013016167', '-1.0 3.7013016167 -7.51462224238', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-1.17013016167 0.948537775762 3.0', '-1.0 0.298698383296 13.5146222424', '-1.10514622242 2.0 20.013016167', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-1.17013016167 0.948537775762 3.0', '-1.0 0.298698383296 -7.51462224238', '-1.0 0.298698383296 13.5146222424', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-1.0 3.7013016167 13.5146222424', '-1.10514622242 2.0 20.013016167', '-0.894853777576 2.0 20.013016167', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-0.82986983833 0.948537775762 3.0', '-0.894853777576 2.0 20.013016167', '-1.0 0.298698383296 13.5146222424', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-1.17013016167 0.948537775762 3.0', '-1.10514622242 2.0 -14.013016167', '-1.0 0.298698383296 -7.51462224238', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-0.894853777576 2.0 20.013016167', '-0.82986983833 0.948537775762 3.0', '-0.82986983833 3.05146222424 3.0', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-1.0 0.298698383296 13.5146222424', '-0.894853777576 2.0 20.013016167', '-1.10514622242 2.0 20.013016167', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-0.82986983833 0.948537775762 3.0', '-1.0 0.298698383296 -7.51462224238', '-0.894853777576 2.0 -14.013016167', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-0.82986983833 3.05146222424 3.0', '-1.0 3.7013016167 -7.51462224238', '-1.0 3.7013016167 13.5146222424', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-0.894853777576 2.0 -14.013016167', '-0.82986983833 3.05146222424 3.0', '-0.82986983833 0.948537775762 3.0', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-1.0 3.7013016167 -7.51462224238', '-0.894853777576 2.0 -14.013016167', '-1.10514622242 2.0 -14.013016167', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-1.17013016167 3.05146222424 3.0', '-1.10514622242 2.0 20.013016167', '-1.0 3.7013016167 13.5146222424', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-1.17013016167 3.05146222424 3.0', '-1.0 3.7013016167 13.5146222424', '-1.0 3.7013016167 -7.51462224238', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-1.10514622242 2.0 20.013016167', '-1.17013016167 3.05146222424 3.0', '-1.17013016167 0.948537775762 3.0', '@trianglelist color=red1 alpha=0.250000 master={points} nobutton', '-1.0 0.298698383296 -7.51462224238', '-1.10514622242 2.0 -14.013016167', '-0.894853777576 2.0 -14.013016167']
exp_subdivide = \
[((1, 0, 0), (0.89442719099991586, 0.0, 0.44721359549995793), (0.89442719099991586, 0.44721359549995793, 0.0)), ((0.89442719099991586, 0.0, 0.44721359549995793), (0.89442719099991586, 0.44721359549995793, 0.0), (0.57735026918962573, 0.57735026918962573, 0.57735026918962573)), ((0.89442719099991586, 0.0, 0.44721359549995793), (0.44721359549995793, 0.0, 0.89442719099991586), (0.57735026918962573, 0.57735026918962573, 0.57735026918962573)), ((0.44721359549995793, 0.0, 0.89442719099991586), (0.0, 0.44721359549995793, 0.89442719099991586), (0.57735026918962573, 0.57735026918962573, 0.57735026918962573)), ((0.44721359549995793, 0.0, 0.89442719099991586), (0, 0, 1), (0.0, 0.44721359549995793, 0.89442719099991586)), ((0.89442719099991586, 0.44721359549995793, 0.0), (0.57735026918962573, 0.57735026918962573, 0.57735026918962573), (0.44721359549995793, 0.89442719099991586, 0.0)), ((0.44721359549995793, 0.89442719099991586, 0.0), (0, 1, 0), (0.0, 0.89442719099991586, 0.44721359549995793)), ((0.44721359549995793, 0.89442719099991586, 0.0), (0.0, 0.89442719099991586, 0.44721359549995793), (0.57735026918962573, 0.57735026918962573, 0.57735026918962573)), ((0.0, 0.89442719099991586, 0.44721359549995793), (0.0, 0.44721359549995793, 0.89442719099991586), (0.57735026918962573, 0.57735026918962573, 0.57735026918962573))]

#run tests if called from command line
if __name__ == "__main__":
    main()
