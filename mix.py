import argparse
import glob
import h5py
import numpy as np
import sys
import tqdm
from sklearn.neighbors import KDTree


def create_libraries(path,binning):

    libs_mjj = {}
    libs_j2pt = {}
    libs_j2eta = {}
    libs_j2reco = {}
    libs_j2kl = {}
    evts_mjj = {}
    evts_deta = {}
    evts_j1pt = {}
    evts_j1eta = {}
    evts_j1reco = {}
    evts_j1kl = {}
    evts_j2pt = {}
    evts_j2eta = {}
    evts_j2reco = {}
    evts_j2kl = {}

    branches = ['mJJ', 'DeltaEtaJJ', 'j1Pt', 'j1Eta', 'j1Phi', 'j1M',
                'j2Pt', 'j2Eta', 'j2Phi', 'j2M', 'j1RecoLoss', 'j1KlLoss',
                'j2RecoLoss', 'j2KlLoss']

    idxs = {}

    kdtrees = {}
    
    for i,filename in enumerate(glob.glob(path+"/*h5")):
        with h5py.File(filename, "r") as f:
            features = f['eventFeatures'][()]
            # Get the indices of the featureNames when opening the first file
            if len(idxs) == 0:
                featureNames = f['eventFeatureNames'][()].astype(np.str)
                for b in branches:
                    idxs[b] = np.argwhere(featureNames == b)[0][0]
                    
            for b,lower in enumerate(binning): 
                if b ==	len(binning)-1:
                    upper = 1e9
                else:
                    upper = binning[b+1]

                # Sorting events according to the bins
                tmp_features = features[ (features[:,idxs['mJJ']] > lower ) & (features[:,idxs['mJJ']] <= upper )]

                #print('Bin',b,'contains',len(tmp_features),'events')
                if b not in evts_mjj:
                    evts_mjj[b] = tmp_features[:,idxs['mJJ']]
                    evts_deta[b] = tmp_features[:,idxs['DeltaEtaJJ']]
                    evts_j1pt[b] = np.log(tmp_features[:,idxs['j1Pt']])
                    evts_j1eta[b] = tmp_features[:,idxs['j1Eta']]
                    evts_j1reco[b] = tmp_features[:,idxs['j1RecoLoss']]
                    evts_j1kl[b] = tmp_features[:,idxs['j1KlLoss']]
                    evts_j2pt[b] = np.log(tmp_features[:,idxs['j2Pt']])
                    evts_j2eta[b] = tmp_features[:,idxs['j2Eta']]
                    evts_j2reco[b] = tmp_features[:,idxs['j2RecoLoss']]
                    evts_j2kl[b] = tmp_features[:,idxs['j2KlLoss']]
                else:
                    evts_mjj[b] = np.concatenate((evts_mjj[b],tmp_features[:,idxs['mJJ']]),axis=0)
                    evts_deta[b] = np.concatenate((evts_deta[b],tmp_features[:,idxs['DeltaEtaJJ']]),axis=0)
                    evts_j1pt[b] = np.concatenate((evts_j1pt[b],np.log(tmp_features[:,idxs['j1Pt']])),axis=0)
                    evts_j1eta[b] = np.concatenate((evts_j1eta[b],tmp_features[:,idxs['j1Eta']]),axis=0)
                    evts_j1reco[b] = np.concatenate((evts_j1reco[b],tmp_features[:,idxs['j1RecoLoss']]),axis=0)
                    evts_j1kl[b] = np.concatenate((evts_j1kl[b],tmp_features[:,idxs['j1KlLoss']]),axis=0)
                    evts_j2pt[b] = np.concatenate((evts_j2pt[b],np.log(tmp_features[:,idxs['j2Pt']])),axis=0)
                    evts_j2eta[b] = np.concatenate((evts_j2eta[b],tmp_features[:,idxs['j2Eta']]),axis=0)
                    evts_j2reco[b] = np.concatenate((evts_j2reco[b],tmp_features[:,idxs['j2RecoLoss']]),axis=0)
                    evts_j2kl[b] = np.concatenate((evts_j2kl[b],tmp_features[:,idxs['j2KlLoss']]),axis=0)

                # Creating a library per bin that corresponds to the inverse
                tmp_features = features[ (features[:,idxs['mJJ']] <= lower ) | (features[:,idxs['mJJ']] > upper )]
                if b not in libs_mjj:
                    libs_j2pt[b] = np.log(tmp_features[:,idxs['j2Pt']])
                    libs_j2eta[b] = tmp_features[:,idxs['j2Eta']]
                    libs_j2reco[b] = tmp_features[:,idxs['j2RecoLoss']]
                    libs_j2kl[b] = tmp_features[:,idxs['j2KlLoss']]
                else:
                    libs_j2pt[b] = np.concatenate((libs_j2pt[b],np.log(tmp_features[:,idxs['j2Pt']])),axis=0)
                    libs_j2eta[b] = np.concatenate((libs_j2eta[b],tmp_features[:,idxs['j2Eta']]),axis=0)
                    libs_j2reco[b] = np.concatenate((libs_j2reco[b],tmp_features[:,idxs['j2RecoLoss']]),axis=0)
                    libs_j2kl[b] = np.concatenate((libs_j2kl[b],tmp_features[:,idxs['j2KlLoss']]),axis=0)



    final_arr = None

    for b,lower in enumerate(binning):    
       print('Bin',b,'contains',len(evts_mjj[b]))

    
    for b,lower in enumerate(binning):
        #if b > 1:
        #    break

        data_for_kdtree = np.stack((libs_j2pt[b],libs_j2eta[b]),axis=-1)
        data_in_bin = np.stack((evts_j2pt[b],evts_j2eta[b]),axis=-1)

        kdtrees[b] = KDTree(data_for_kdtree)        
        dist,ind = kdtrees[b].query(data_in_bin, k=1)
        flat_ind = ind.flatten()

        #print("Data in bin",b)
        #print(data_in_bin.shape)
        #print("Length of lib used for bin",b)
        #print(data_for_kdtree.shape)
        
        evts_mjj[b] = np.expand_dims(evts_mjj[b],axis=1)
        evts_deta[b] = np.expand_dims(evts_deta[b],axis=1)
        evts_j1pt[b] = np.expand_dims(np.exp(evts_j1pt[b]),axis=1)
        evts_j1eta[b] = np.expand_dims(evts_j1eta[b],axis=1)
        evts_j1reco[b] = np.expand_dims(evts_j1reco[b],axis=1)
        evts_j1kl[b] = np.expand_dims(evts_j1kl[b],axis=1)
        evts_j2pt[b] = np.expand_dims(np.exp(evts_j2pt[b]),axis=1)
        evts_j2eta[b] = np.expand_dims(evts_j2eta[b],axis=1)
        replaced_j2reco = np.expand_dims(libs_j2reco[b][flat_ind],axis=1)
        replaced_j2kl = np.expand_dims(libs_j2kl[b][flat_ind],axis=1)

        #print(replaced_j2reco.shape)
        #print(replaced_j2kl.shape)
        #print(evts_j2pt[b].shape)
        
        final_features_in_bin = np.squeeze(np.stack((evts_mjj[b],evts_deta[b],evts_j1pt[b],evts_j1eta[b],evts_j1reco[b],evts_j1kl[b],\
                                                     evts_j2pt[b],evts_j2eta[b],replaced_j2reco,replaced_j2kl),axis=-1),axis=1)
        #print(final_features_in_bin)
        #print(final_features_in_bin.shape)

        if b == 0:
            final_arr = final_features_in_bin
        else:
            final_arr = np.concatenate((final_arr,final_features_in_bin),axis=0)

    #print(final_arr.shape)

    ofile = h5py.File('mixed_bkg.h5', 'w')
    ofile.create_dataset('eventFeatures', data=final_arr)
    ofile.create_dataset('eventFeatureNames', data=['mJJ', 'DeltaEtaJJ', 'j1Pt', 'j1Eta', 'j1RecoLoss', 'j1KlLoss',\
                                                    'j2Pt', 'j2Eta', 'j2RecoLoss', 'j2KlLoss'])
    ofile.close()

        
    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser("")
    parser.add_argument('--eventlibrary', type=str, default="X", help="")
    options = parser.parse_args()

    binning = [1450, 1529, 1604, 1681, 1761, 1844, 1930, 2019, 
               2111, 2206, 2305, 2406, 2512, 2620, 2733, 2849, 2969, 3093,
               3221, 3353, 3490, 3632, 3778, 3928, 4084, 4245, 4411, 4583,
               4760, 4943, 5132, 5327, 5527]

    #binning = [1450, 2450, 3450, 4450, 5450]

    create_libraries(options.eventlibrary, binning)

    
