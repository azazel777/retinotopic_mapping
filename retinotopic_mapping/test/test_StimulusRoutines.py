import os
import unittest
import retinotopic_mapping.StimulusRoutines as sr

curr_folder = os.path.dirname(os.path.realpath(__file__))
os.chdir(curr_folder)

class TestSimulation(unittest.TestCase):

    def setUp(self):
        import retinotopic_mapping.MonitorSetup as ms

        # Setup monitor/indicator objects
        self.monitor = ms.Monitor(resolution=(1200,1600), dis=15.,
                                   mon_width_cm=40., mon_height_cm=30.,
                                   C2T_cm=15.,C2A_cm=20., mon_tilt=30., downsample_rate=10)
        # import matplotlib.pyplot as plt
        # self.monitor.plot_map()
        # plt.show()

        self.indicator = ms.Indicator(self.monitor, width_cm = 3., height_cm = 3., position = 'northeast',
                                      is_sync = True, freq = 1.)

    def test_get_circle_mask(self):
        import numpy as np

        alt = np.arange(-30., 30., 1.)[::-1]
        azi = np.arange(-30., 30., 1.)
        azi_map, alt_map = np.meshgrid(azi, alt)
        cm = sr.get_circle_mask(map_alt=alt_map, map_azi=azi_map, center=(0., 10.), radius=10.)
        # import matplotlib.pyplot as plt
        # plt.imshow(cm)
        # plt.show()
        assert (cm[28, 49] == 1)
        cm = sr.get_circle_mask(map_alt=alt_map, map_azi=azi_map, center=(10., 0.), radius=10.)
        # import matplotlib.pyplot as plt
        # plt.imshow(cm)
        # plt.show()
        assert (cm[10, 30] == 1)

    def test_get_grating(self):
        import numpy as np

        alt = np.arange(-30., 30., 1.)[::-1]
        azi = np.arange(-30., 30., 1.)
        azi_map, alt_map = np.meshgrid(azi, alt)

        grating = sr.get_grating(alt_map=alt_map, azi_map=azi_map, dire=315.,
                                 spatial_freq=0.04, center=(0., 0.), phase=0.,
                                 contrast=1.)
        assert (grating[34, 29] < 0.827)
        assert (grating[34, 29] > 0.825)

        # import matplotlib.pyplot as plt
        # f, (ax) = plt.subplots(1)
        # ax.imshow(grating, cmap='gray')
        # plt.show()

    def test_get_grid_locations(self):
        monitor_azi = self.monitor.deg_coord_x
        monitor_alt = self.monitor.deg_coord_y
        grid_locs = sr.get_grid_locations(subregion=[-20., -10., 30., 90.], grid_space=[10., 10.],
                                          monitor_azi=monitor_azi, monitor_alt=monitor_alt,
                                          is_include_edge=True, is_plot=False)
        assert (len(grid_locs) == 14)

    # UNIFORM CONTRAST TESTS
    # ======================
    def test_UC_generate_movie_by_index(self):
        # Setup Uniform Contrast Objects
        uc = sr.UniformContrast(monitor=self.monitor, indicator=self.indicator, duration=0.1,
                                color=1., pregap_dur=1., postgap_dur=1.5, background=0.,
                                coordinate='degree')

        uc_full_seq, uc_full_dict = uc.generate_movie_by_index()

        assert (uc_full_seq.shape == (2, 120, 160))
        assert (len(uc_full_dict['stimulation']['index_to_display']) == 156)

        frames_unique = uc_full_dict['stimulation']['frames_unique']
        all_frames = []
        for ind in uc_full_dict['stimulation']['index_to_display']:
            all_frames.append(frames_unique[ind])

        # Parameters defining where the frame blocks should start and end
        ref_rate = self.monitor.refresh_rate
        pregap_end = uc.pregap_frame_num
        on_end = pregap_end + int(uc.duration*ref_rate)
        postgap_end = on_end + uc.postgap_frame_num

        for i in range(pregap_end):
            assert (all_frames[i] == (0., -1.))

        for i in range(pregap_end, on_end):
            assert (all_frames[i] == (1., 1.))

        for i in range(on_end, postgap_end):
            assert (all_frames[i] == (0., -1.))

    # FLASHING CIRCLE TESTS #
    # ===================== #
    def test_FC_generate_movie_by_index(self):

        fc = sr.FlashingCircle(monitor=self.monitor,
                                    indicator=self.indicator,
                                    center=(10., 90.), flash_frame_num=30,
                                    color=-1., pregap_dur=0.5, postgap_dur=1.2,
                                    background=1., coordinate='degree')

        fc_full_seq, fc_full_dict = fc.generate_movie_by_index()

        assert (fc_full_seq.shape == (2, 120, 160))

        assert (len(fc_full_dict['stimulation']['index_to_display']) == 132)

        frames_unique = fc_full_dict['stimulation']['frames_unique']
        frames = []
        for ind in fc_full_dict['stimulation']['index_to_display']:
            frames.append(frames_unique[ind])

        # Parameters defining where the frame blocks should start and end
        pregap_end = fc.pregap_frame_num
        flash_frames= fc.flash_frame_num
        flashing_end = pregap_end + flash_frames
        postgap_end = flashing_end + fc.postgap_frame_num

        for i in range(pregap_end):
            assert (frames[i] == (0., -1.))

        for i in range(pregap_end, flashing_end):
            assert (frames[i] == (1., 1.))

        for i in range(flashing_end, postgap_end):
            assert (frames[i] == (0., -1.))

        assert (fc_full_seq[1, 39, 124] == -1)
        # import matplotlib.pyplot as plt
        # f, (ax) = plt.subplots(1)
        # ax.imshow(fc_full_seq[1])
        # plt.show()

    def test_FC_generate_movie(self):

        fc = sr.FlashingCircle(monitor=self.monitor,
                                    indicator=self.indicator,
                                    center=(10., 90.), flash_frame_num=30,
                                    color=-1., pregap_dur=0.1, postgap_dur=1.0,
                                    background=1., coordinate='degree')

        fc_full_seq, fc_full_dict = fc.generate_movie()

        assert (fc_full_seq.shape == (96, 120, 160))
        assert (len(fc_full_dict['stimulation']['frames']) == 96)

        frames = fc_full_dict['stimulation']['frames']
        # print frames

        # Parameters defining where the frame blocks should start and end
        pregap_end = fc.pregap_frame_num
        flash_frames = fc.flash_frame_num
        flashing_end = pregap_end + flash_frames
        postgap_end = flashing_end + fc.postgap_frame_num

        for i in range(pregap_end):
            assert (frames[i] == (0., -1.))

        for i in range(pregap_end, flashing_end):
            assert (frames[i] == (1., 1.))

        for i in range(flashing_end, postgap_end):
            assert (frames[i] == (0., -1.))

        assert (fc_full_seq[6, 39, 124] == -1.)

        # import matplotlib.pyplot as plt
        # f, (ax) = plt.subplots(1)
        # ax.imshow(fc_full_seq[6])
        # plt.show()

    # SPARSE NOISE TESTS #
    # ================== #
    def test_SN_generate_display_index(self):
        sn = sr.SparseNoise(monitor=self.monitor, indicator=self.indicator,
                            background=0., coordinate='degree', grid_space=(10.,10.),
                            probe_size=(10.,10.), probe_orientation=0., probe_frame_num=6,
                            subregion=[10, 20, 0., 60.], sign='ON', iteration=1, pregap_dur=0.1,
                            postgap_dur=0.2, is_include_edge=True)

        frames_unique, index_to_display = sn._generate_display_index()
        # print '\n'.join([str(f) for f in frames_unique])
        # print index_to_display
        assert (index_to_display[:6] == [0, 0, 0, 0, 0, 0])
        assert (index_to_display[-12:] == [0] * 12)
        # print max(index_to_display)
        # print len(frames_unique)
        assert (max(index_to_display) == len(frames_unique) -1)
        probe_num = (len(index_to_display) - 18) / 6
        for probe_ind in range(probe_num):
            assert (len(set(index_to_display[6 + probe_ind * 6: 9 + probe_ind * 6])) == 1)
            assert (len(set(index_to_display[9 + probe_ind * 6: 12 + probe_ind * 6])) == 1)
            assert (index_to_display[9 + probe_ind * 6] - index_to_display[8 + probe_ind * 6] == 1)

    def test_SN_get_probe_index_for_one_iter_on_off(self):
        import numpy as np
        sn = sr.SparseNoise(monitor=self.monitor, indicator=self.indicator,
                            background=0., coordinate='degree', grid_space=(5., 5.),
                            probe_size=(5., 5.), probe_orientation=0., probe_frame_num=6,
                            subregion=[-30, 30, -10., 90.], sign='ON-OFF', iteration=2)
        frames_unique = sn._generate_frames_for_index_display()
        probe_ind = sn._get_probe_index_for_one_iter_on_off(frames_unique)
        for j in range(len(probe_ind) - 1):
            probe_loc_0 = frames_unique[probe_ind[j]]
            probe_loc_1 = frames_unique[probe_ind[j + 1]]
            assert(not np.array_equal(probe_loc_0, probe_loc_1))

    def test_SN_generate_display_index2(self):
        import numpy as np
        sn = sr.SparseNoise(monitor=self.monitor, indicator=self.indicator,
                            background=0., coordinate='degree', grid_space=(10., 10.),
                            probe_size=(10., 10.), probe_orientation=0., probe_frame_num=8,
                            subregion=[-10, 10, 45., 55.], sign='ON-OFF', iteration=2,
                            pregap_dur=0.5, postgap_dur=0.3, is_include_edge=True)

        frames_unique, index_to_display = sn._generate_display_index()
        assert (index_to_display[:30] == [0] * 30)
        assert (index_to_display[-18:] == [0] * 18)
        assert (max(index_to_display) == len(frames_unique) - 1)

        frame_num_iter = len(index_to_display) / 2
        assert (index_to_display[frame_num_iter - 18: frame_num_iter + 30] == [0] * 48)
        probe_num = (len(index_to_display[:frame_num_iter]) - 30) / 6
        for probe_ind in range(probe_num):
            assert (len(set(index_to_display[30 + probe_ind * 8: 34 + probe_ind * 8])) == 1)
            assert (len(set(index_to_display[34 + probe_ind * 8: 38 + probe_ind * 8])) == 1)
            assert (np.array_equal(frames_unique[index_to_display[33 + probe_ind * 8]][1],
                                   frames_unique[index_to_display[34 + probe_ind * 8]][1]))

    def test_SN_generate_movie_by_index(self):
        sn = sr.SparseNoise(monitor=self.monitor, indicator=self.indicator,
                            background=0., coordinate='degree', grid_space=(10., 10.),
                            probe_size=(10., 10.), probe_orientation=0., probe_frame_num=6,
                            subregion=[-20., -10., 30., 90.], sign='ON', iteration=1, pregap_dur=0.1,
                            postgap_dur=0.2, is_include_edge=True)
        mov_unique, _ = sn.generate_movie_by_index()
        import numpy as np
        # import matplotlib.pyplot as plt
        # plt.imshow(np.max(mov_unique, axis=0))
        # plt.show()
        assert (np.max(mov_unique, axis=0)[66, 121] == 1)

    def test_SN_generate_movie(self):
        sn = sr.SparseNoise(monitor=self.monitor, indicator=self.indicator,
                            background=0., coordinate='degree', grid_space=(10., 10.),
                            probe_size=(10., 10.), probe_orientation=0., probe_frame_num=6,
                            subregion=[-20., -10., 30., 90.], sign='OFF', iteration=1, pregap_dur=0.1,
                            postgap_dur=0.2, is_include_edge=True)
        mov_unique, _ = sn.generate_movie_by_index()
        import numpy as np
        # import matplotlib.pyplot as plt
        # plt.imshow(np.min(mov_unique, axis=0))
        # plt.show()
        assert (np.min(mov_unique, axis=0)[92, 38] == -1)

    # DRIFTING GRATING CIRCLE TESTS #
    # ============================= #
    def test_DGC_generate_frames(self):
        dgc = sr.DriftingGratingCircle(monitor=self.monitor, indicator=self.indicator, background=0.,
                                       coordinate='degree', center=(10., 90.), sf_list=(0.02, 0.04),
                                       tf_list=(1.0,), dire_list=(45.,), con_list=(0.8,), radius_list=(20.,),
                                       block_dur=2., midgap_dur=1., iteration=2, pregap_dur=1.5,
                                       postgap_dur=3.)

        frames = dgc.generate_frames()
        assert (len(frames) == 930)
        assert ([f[0] for f in frames[0:90]] == [0] * 90)
        assert ([f[0] for f in frames[210:270]] == [0] * 60)
        assert ([f[0] for f in frames[390:450]] == [0] * 60)
        assert ([f[0] for f in frames[570:630]] == [0] * 60)
        assert ([f[0] for f in frames[750:930]] == [0] * 180)
        assert ([f[8] for f in frames[0:90]] == [-1.] * 90)
        assert ([f[8] for f in frames[210:270]] == [-1.] * 60)
        assert ([f[8] for f in frames[390:450]] == [-1.] * 60)
        assert ([f[8] for f in frames[570:630]] == [-1.] * 60)
        assert ([f[8] for f in frames[750:930]] == [-1.] * 180)

        assert ([f[0] for f in frames[90:210]] == [1] * 120)
        assert ([f[0] for f in frames[270:390]] == [1] * 120)
        assert ([f[0] for f in frames[450:570]] == [1] * 120)
        assert ([f[0] for f in frames[630:750]] == [1] * 120)
        assert (frames[90][8] == 1.)
        assert ([f[8] for f in frames[91:150]] == [0.] * 59)
        assert (frames[150][8] == 1.)
        assert ([f[8] for f in frames[151:210]] == [0.] * 59)
        assert (frames[270][8] == 1.)
        assert ([f[8] for f in frames[271:330]] == [0.] * 59)
        assert (frames[330][8] == 1.)
        assert ([f[8] for f in frames[331:390]] == [0.] * 59)
        assert (frames[450][8] == 1.)
        assert ([f[8] for f in frames[451:510]] == [0.] * 59)
        assert (frames[510][8] == 1.)
        assert ([f[8] for f in frames[511:570]] == [0.] * 59)
        assert (frames[630][8] == 1.)
        assert ([f[8] for f in frames[631:690]] == [0.] * 59)
        assert (frames[690][8] == 1.)
        assert ([f[8] for f in frames[691:750]] == [0.] * 59)

    def test_DGC__generate_frames_for_index_display_condition(self):
        dgc = sr.DriftingGratingCircle(monitor=self.monitor, indicator=self.indicator,
                                       block_dur=2., sf_list=(0.04,), tf_list=(2.0,),
                                       dire_list=(45.,), con_list=(0.8,), radius_list=(10.,),
                                       midgap_dur=0.1, pregap_dur=0.5, postgap_dur=0.2,
                                       iteration=2)

        conditions = dgc._generate_all_conditions()
        # print len(conditions)
        assert (len(conditions) == 1)
        frames_unique_condi, index_to_display_condi = dgc._generate_frames_for_index_display_condition(conditions[0])
        assert (index_to_display_condi == range(30) * 4)
        assert (max(index_to_display_condi) == len(frames_unique_condi) - 1)
        # print '\n'.join([str(f) for f in frames_unique_condi])
        assert ([f[0] for f in frames_unique_condi] == [1] * 30)
        assert (frames_unique_condi[0][1] == 1)
        assert (frames_unique_condi[0][8] == 1.)
        assert ([f[1] for f in frames_unique_condi[1:]] == [0] * 29)
        assert ([f[8] for f in frames_unique_condi[1:]] == [0.] * 29)

    def test_DGC_generate_frames_unique_and_condi_ind_dict(self):
        dgc = sr.DriftingGratingCircle(monitor=self.monitor, indicator=self.indicator,
                                       block_dur=2., sf_list=(0.04,), tf_list=(1., 3.0,),
                                       dire_list=(45., 90.), con_list=(0.8,), radius_list=(10.,),
                                       midgap_dur=0.1, pregap_dur=0.5, postgap_dur=0.2,
                                       iteration=2)
        frames_unique, condi_ind_in_frames_unique = dgc._generate_frames_unique_and_condi_ind_dict()
        assert (len(condi_ind_in_frames_unique) == 4)
        assert (set(condi_ind_in_frames_unique.keys()) == set(['condi_0000', 'condi_0001', 'condi_0002', 'condi_0003']))
        assert (len(frames_unique) == 161)

        import numpy as np
        for cond, ind in condi_ind_in_frames_unique.items():
            assert (len(ind) == 120)
            assert (ind[0] % 20 == 1)
            assert (len(np.unique(ind)) == 60 or len(np.unique(ind)) == 20)
            # print '\ncond'
            # print ind

    def test_DGC_generate_display_index(self):
        dgc = sr.DriftingGratingCircle(monitor=self.monitor, indicator=self.indicator,
                                       block_dur=2., sf_list=(0.04,), tf_list=(1., 3.0,),
                                       dire_list=(45., 90.), con_list=(0.8,), radius_list=(10.,),
                                       midgap_dur=0.1, pregap_dur=0.5, postgap_dur=0.2,
                                       iteration=2)
        frames_unique, index_to_display = dgc._generate_display_index()
        # print '\n'.join([str(f) for f in frames_unique])
        assert (len(frames_unique) == 161)
        assert (max(index_to_display) == len(frames_unique) - 1)
        # print len(index_to_display)
        assert (len(index_to_display) == 1044)

    # def test_get_sparse_loc_num_per_frame(self):
    #     ppf = sr.get_sparse_loc_num_per_frame(min_alt=-20., max_alt=40., min_azi=-10.,
    #                                           max_azi=120., minimum_dis=20.)
    #     print ppf

    def test_LSN_generate_all_probes(self):
        lsn = sr.LocallySparseNoise(monitor=self.monitor, indicator=self.indicator,
                                    min_distance=20., background=0., coordinate='degree',
                                    grid_space=(10., 10.), probe_size=(10., 10.),
                                    probe_orientation=0., probe_frame_num=6, subregion=[-10., 10., 0., 30.],
                                    sign='ON', iteration=1, pregap_dur=2., postgap_dur=3.,
                                    is_include_edge=True)

        all_probes = lsn._generate_all_probes()
        all_probes = [tuple(p) for p in all_probes]
        assert (set(all_probes) == {
                                    (-10., 0., 1.), (0., 0., 1.), (10., 0., 1.),
                                    (-10., 10., 1.), (0., 10., 1.), (10., 10., 1.),
                                    (-10., 20., 1.), (0., 20., 1.), (10., 20., 1.),
                                    (-10., 30., 1.), (0., 30., 1.), (10., 30., 1.),
                                    })

    def test_LSN_generate_probe_locs_one_frame(self):
        lsn = sr.LocallySparseNoise(monitor=self.monitor, indicator=self.indicator,
                                    min_distance=20., background=0., coordinate='degree',
                                    grid_space=(10.,10.), probe_size=(10.,10.),
                                    probe_orientation=0., probe_frame_num=6, subregion=[-10., 20., 0., 60.],
                                    sign='ON', iteration=1, pregap_dur=2., postgap_dur=3.,
                                    is_include_edge=True)

        all_probes = lsn._generate_all_probes()
        probes_one_frame = lsn._generate_probe_locs_one_frame(all_probes)

        import itertools
        import numpy as np
        for (p0, p1) in itertools.combinations(probes_one_frame, r=2):
            curr_dis = np.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) **2)
            # print (p0, p1), curr_dis
            assert (curr_dis > 20.)

    def test_LSN_generate_probe_sequence_one_iteration(self):
        lsn = sr.LocallySparseNoise(monitor=self.monitor, indicator=self.indicator,
                                    min_distance=20., background=0., coordinate='degree',
                                    grid_space=(10., 10.), probe_size=(10., 10.),
                                    probe_orientation=0., probe_frame_num=6, subregion=[-10., 20., 0., 60.],
                                    sign='ON-OFF', iteration=1, pregap_dur=2., postgap_dur=3.,
                                    is_include_edge=True)

        all_probes = lsn._generate_all_probes()
        frames = lsn._generate_probe_sequence_one_iteration(all_probes=all_probes, is_redistribute=False)
        print '\n'.join([str(f) for f in frames])
        print [len(f) for f in frames]
        assert (sum([len(f) for f in frames]) == len(all_probes))
        # todo: finish this

    def test_LSN_is_fit(self):
        # todo: finish this
        pass

    def test_LSN_redistribute_one_probe(self):
        # todo: finish this
        pass

    def test_LSN_redistribute_probes(self):
        lsn = sr.LocallySparseNoise(monitor=self.monitor, indicator=self.indicator,
                                    min_distance=20., background=0., coordinate='degree',
                                    grid_space=(10., 10.), probe_size=(10., 10.),
                                    probe_orientation=0., probe_frame_num=6, subregion=[-10., 20., 0., 60.],
                                    sign='ON-OFF', iteration=1, pregap_dur=2., postgap_dur=3.,
                                    is_include_edge=True)

        all_probes = lsn._generate_all_probes()
        frames = lsn._generate_probe_sequence_one_iteration(all_probes=all_probes, is_redistribute=True)
        print '\n'.join([str(f) for f in frames])
        print [len(f) for f in frames]
        assert (sum([len(f) for f in frames]) == len(all_probes))
        # todo: finish this


if __name__ == '__main__':
    unittest.main(verbosity=2.)