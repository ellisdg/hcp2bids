# -*- coding: utf-8 -*-
"""
Created on Aug 2016
Script to save HCP data into bids format. folowing script creates directory struc
ture and renames all files as per BIDS standard.
@author: Suyash B
"""

import os, glob, shutil
import re, json, numpy
import nibabel as ni



def touch(fname):
    if os.path.exists(fname):
        os.utime(fname, None)
    else:
        open(fname, 'a').close()

def FourDimImg(image, destinationpath_3d, outputfilename):
    #outputfilename= sub-285345_run-02_magnitude2
    #this function handles conversion from 4d to 3d along with saving output with bids std name
    img = ni.load(image)
    destination_path = destinationpath_3d
    images = ni.four_to_three(img)
    outputfilenamepattern = outputfilename + '{:01d}.nii.gz'
    for i, img_3d in enumerate(images):
        i = i +1
        output_filename = outputfilenamepattern.format(i)
        output_path = os.path.join(destination_path, output_filename)
        ni.save(img_3d, output_path)
    os.remove(image)
    return img_3d

#d = '/work/04275/suyashdb/lonestar/test_hcp/'
def hcp2bids(input_dir, output_dir):
    sub_dir = [os.path.join(input_dir,o) for o in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir,o))]
    for subjects in sub_dir:
        subj_raw =  os.path.join(subjects, 'unprocessed/3T/')
        print(subj_raw)
        #path_bids = '/scratch/04275/suyashdb/hcp/%s/' %subject
        bids = os.path.join(output_dir, subjects.split('/')[-1])
        #bids = subjects + '/bids/'
        os.mkdir(bids)
        fmap = os.path.join(bids, 'fmap/')
        print('fmap')
        func = os.path.join(bids, 'func/')
        anat = os.path.join(bids, 'anat/')
        dwi =  os.path.join(bids,'dwi/')
        os.mkdir(fmap)
        print("fmap path",fmap)
        os.mkdir(func)
        os.mkdir(anat)
        os.mkdir(dwi)
        fieldmaplist = glob.glob(os.path.join(subj_raw, '*/*FieldMap*'))
        for fieldmap in fieldmaplist:
            parentdir = os.path.split(os.path.dirname(fieldmap))[1]
            dst = fmap + parentdir +'_'+ os.path.split(fieldmap)[1]
            shutil.copy(fieldmap, dst)
        print("done with fMAPs for --", subjects)
        func_list = glob.glob(os.path.join(subj_raw, 't*/*tfMRI*'))
        for func_data in func_list:
            parentdir = os.path.split(os.path.dirname(func_data))[1]
            dst = func + parentdir +'_'+ os.path.split(func_data)[1]
            shutil.move(func_data, dst)
        print("done with func for --", subjects)
        sbref_list = glob.glob(os.path.join(subj_raw, '*/*SBRef*'))
        for sbref in sbref_list:
            parentdir = os.path.split(os.path.dirname(sbref))[1]
            dst = func + parentdir +'_'+ os.path.split(sbref)[1]
            shutil.move(sbref, dst)
        print("done with SBREF's for --", subjects)
        anat_list = glob.glob(os.path.join(subj_raw, 'T*/*3T_T*'))
        for anat_data in anat_list:
            parentdir = os.path.split(os.path.dirname(anat_data))[1]
            dst = anat + parentdir +'_'+ os.path.split(anat_data)[1]
            shutil.move(anat_data, dst)
        print("done with Anat for --", subjects)
        dwi_list = glob.glob(os.path.join(subj_raw, '*/*DWI*'))
        for dwi_data in dwi_list:
            parentdir = os.path.split(os.path.dirname(dwi_data))[1]
            dst = dwi + parentdir +'_'+ os.path.split(dwi_data)[1]
            shutil.move(dwi_data, dst)
        print("done with DWI's for --", subjects)
        dwi_subj_raw = os.path.join(subjects, 'bids')
        dwi_sbref_list = glob.glob(os.path.join(func,'*DWI*SBRef*'))
        for sbref in dwi_sbref_list:
            parentdir = os.path.split(os.path.dirname(sbref))[1]
            dst = dwi +'_'+ os.path.split(sbref)[1]
            shutil.move(sbref, dst)
        ''' Sort nifti files and Rename all files as per bids'''
        nifti_func_list = glob.glob(os.path.join(func, '*fMRI*.nii.gz'))
        print("path where nifti files are searched -", os.path.join(func, '*fMRI*.nii.gz'))
        for nifti_func_file in nifti_func_list:
            filename_split = nifti_func_file.split('_')
            task = filename_split[2]
            print(task)
            acq = filename_split[3]
            sub = filename_split[4].lower()
            if task in ['REST1', 'REST2']:
                #m = re.match(r"([a-zA-Z]+)([0-9]+)",task)
                #run = m.group(2)
                run = '0' + str(task[-1])
                task = str(task[:-1])
                # print("This is task form rest loop - ", task)
            tail = filename_split[-1]
            if task not in ['REST', 'REST2']:
                if 'SBRef' in tail:
                    filename = 'sub-' + sub + '_' + 'task-' + task + '_' +  'acq-' + acq + '_' + tail.lower()
                else:
                    filename = 'sub-' + sub + '_' + 'task-' + task + '_' +  'acq-' + acq + '_bold' + tail[-7:]
            else:
                filename = 'sub-' + sub + '_' + 'task-' + task + '_' +  'acq-' + acq +'_'+ 'run-' + run + '_' + tail.lower()
            path_filename = func + filename
            shutil.move(nifti_func_file, path_filename)
            #touch(path_filename[:-6]+ 'json')
            print(filename)
        ''' sort anat files and rename it '''
        #anat = '/Users/suyashdb/Documents/hcp2bids/hcpdata/285446/bids/anat'
        anat_files_list = glob.glob(os.path.join(anat, '*T*.nii.gz'))
        for anat_file in anat_files_list:
            filename_split = anat_file.split('_')
            run = filename_split[2][-1]
            print(filename_split)
            sub = filename_split[3]
            modality = filename_split[5]
            tail = filename_split[-1][-7:]
            filename = 'sub-' + sub + '_' + 'run-0' + run + '_' + modality + tail
            path_filename = anat + filename
            shutil.move(anat_file, path_filename)
            #touch(path_filename[:-6]+ 'json')
            print(filename)
            ##########
        #Sort all nii.gz files in dwi and fmaps '''
        dwi_files_list = glob.glob(os.path.join(dwi, 'Diffusion*DWI*.nii.gz'))
        for dwi_file in dwi_files_list:
            filename_split = dwi_file.split('_')
            print(filename_split)
            sub = filename_split[2]
            acq = filename_split[5].lower() + filename_split[6][:2]
            modality = 'dwi'
            tail = filename_split[-1][-7:]
            filename = 'sub-' + sub + '_' + 'acq-' + acq + '_' + modality + tail
            path_filename = dwi + filename
            shutil.move(dwi_file, path_filename)
            dwi_json_dict = {}
            dwi_json_dict["EffectiveEchoSpacing"] = 0.00078
            dwi_json_dict["TotalReadoutTime"] = 0.111542
            dwi_json_dict["EchoTime"] = 0.08950
            if dwi_file[-9:-7] == 'LR':
                dwi_json_dict["PhaseEncodingDirection"] = "i-"
            else:
                dwi_json_dict["PhaseEncodingDirection"] = "i"
            touch(path_filename[:-6]+ 'json')
            json_file = path_filename[:-6]+ 'json'
            with open(json_file, 'w') as editfile:
                json.dump( dwi_json_dict, editfile, indent = 4)
            shutil.move((dwi_file[:-6]+'bval'), (path_filename[:-6] + 'bval'))
            shutil.move((dwi_file[:-6]+'bvec'), (path_filename[:-6] + 'bvec'))
            print(filename)
        dwisbref_files_list = glob.glob(os.path.join(dwi, '*DWI*SBRef.nii.gz'))
        for dwi_file in dwisbref_files_list:
            filename_split = dwi_file.split('_')
            print(filename_split)
            sub = filename_split[3]
            acq = filename_split[6].lower() + filename_split[7][:2]
            modality = 'sbref'
            tail = filename_split[-1][-7:]
            filename = 'sub-' + sub + '_' + 'acq-' + acq + '_' + modality + tail
            path_filename = dwi + filename
            shutil.move(dwi_file, path_filename)
            print(filename)
            dwi_json_dict = {}
            dwi_json_dict["EffectiveEchoSpacing"] = 0.00078
            dwi_json_dict["TotalReadoutTime"] = 0.111542
            dwi_json_dict["EchoTime"] = 0.08950
            if filename_split[7][:2] == 'LR':
                dwi_json_dict["PhaseEncodingDirection"] = "i-"
            else:
                dwi_json_dict["PhaseEncodingDirection"] = "i"
            touch(path_filename[:-6]+ 'json')
            json_file = path_filename[:-6]+ 'json'
            with open(json_file, 'w') as editfile:
                json.dump( dwi_json_dict, editfile, indent = 4)
        ''' Fmaps'''
        counter = 1
        fmap_files_list = glob.glob(os.path.join(fmap, '*SpinEchoFieldMap*.nii.gz'))
        for fmapfile in fmap_files_list:
            fmap_file = os.path.split(fmapfile)[1]
            filename_split = fmap_file.split('_')
            print(filename_split)
            task = filename_split[1]
            print(task)
            acq = filename_split[2]
            sub = filename_split[3].lower()
            if task in ['REST1', 'REST2']:
                #m = re.match(r"([a-zA-Z]+)([0-9]+)",task)
                #run = m.group(2)
                run = '0' + str(task[-1])
                task = str(task[:-1])
                print("This is task form rest loop - ", task)
            tail = filename_split[-1]
            if task not in ['REST', 'REST2']:
                if 'SBRef' in tail:
                    filename = 'sub-' + sub + '_' + 'task-' + task + '_' +  'acq-' + acq + '_' + tail.lower()
                else:
                    filename = 'sub-' + sub + '_' + 'task-' + task + '_' +  'acq-' + acq + '_bold' + tail[-7:]
            else:
                filename = 'sub-' + sub + '_' + 'task-' + task + '_' +  'acq-' + acq +'_'+ 'run-' + run + '_' + tail.lower()
            print('intended_for - ',filename)
            filename = 'func/'+ filename
            fmap_json_dict = {}
            fmap_json_dict["intended_for"] = filename
            fmap_json_dict["TotalReadoutTime"] = 0.08346
            if fmapfile[-9:-7] == 'LR':
                fmap_json_dict["PhaseEncodingDirection"] = "i-"
            else:
                fmap_json_dict["PhaseEncodingDirection"] = "i"
            #intended_for ={"IntendedFor", filename}
            dir = counter
            hcpfmapfilename = 'sub-' + sub + '_'+ 'dir-' + str(dir) + '_' + 'epi.nii.gz'
            print('hcpfmap_filename',hcpfmapfilename)
            path_filename = fmap + hcpfmapfilename
            shutil.move(fmapfile, path_filename)
            touch(path_filename[:-6]+ 'json')
            json_file = path_filename[:-6]+ 'json'
            with open(json_file, 'w') as editfile:
                json.dump( fmap_json_dict, editfile, indent = 4)
            counter = counter + 1
            print("BIDS format data is at -", output_dir)
        #fmap_magnitude and phasediff
        fmap_files_list = glob.glob(os.path.join(fmap, 'T*Magnitude.nii.gz'))
        run = 1
        for fmapfile in fmap_files_list:
            fmap_file = os.path.split(fmapfile)[1]
            filename_split = fmap_file.split('_')
            acq = filename_split[2]
            sub = filename_split[2]
            run_number = filename_split[1][-1]
            filename = 'sub-' + sub + '_' + 'run-0' + str(run) + '_magnitude'
            FourDimImg(fmapfile, fmap, filename)
            #looking into phasediff image
            filename_phasediff = 'sub-' + sub + '_' + 'run-0' + str(run) + '_phasediff' + '.nii.gz'
            filename_phasediff_path = os.path.join(fmap,filename_phasediff)
            shutil.move(fmapfile.replace('Magnitude', 'Phase'), filename_phasediff_path)
            filename_phasediff_json = filename_phasediff[:-6]+ 'json'
            filename_phasediff_json_path = os.path.join(fmap, filename_phasediff_json)
            touch(filename_phasediff_json_path)
            intended_for_filename = 'anat/sub-' + sub + '_' + 'run-0' + run_number + '_' + filename_split[0] + '.nii.gz'
            print('intended_for - ',intended_for_filename)
            fmap_phasdiff_json_dict = {}
            fmap_phasdiff_json_dict["intended_for"] = intended_for_filename
            if filename_split[0] == 'T1w':
                fmap_phasdiff_json_dict["EchoTime1"] = 0.00214
                fmap_phasdiff_json_dict["EchoTime2"] = 0.00460
            if filename_split[0] == 'T2w':
                fmap_phasdiff_json_dict["EchoTime1"] = 0.00565
                fmap_phasdiff_json_dict["EchoTime2"] = 0.00811
            with open(filename_phasediff_json_path, 'w') as editfile:
                json.dump( fmap_phasdiff_json_dict, editfile, indent = 4)
            run = run + 1


## main.py
get input and output dir from user
hcp2bids('/work/04275/suyashdb/lonestar/test_hcp1/', '/work/04275/suyashdb/lonestar/test_output/')
output_dir = '/work/04275/suyashdb/lonestar/test_output/'
sub_dir = [os.path.join(output_dir,o) for o in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir,o))]
for subjects in sub_dir:
    sub = subjects.split('/')[-1]
    dir_name = 'sub-'+ sub
    dir_name_path = os.path.join(output_dir, dir_name)
    shutil.move(subjects, dir_name_path)


Diffusion requirements - effective echo spacing
Siemens turbo factor is Echo Train length - 78

# TotalReadoutTime = Echo spacing * (ReconMatrixPE - 1)
# TotalReadoutTime = 0.00078 * (143-1) = 0.11154
# https://neurostars.org/t/what-is-the-totalreadouttime-of-hcp-dwi-data/19622

'''
dMRI\DWI_RL_dir95   - TE 0.0895


'''
# fmap_files_list = glob.glob(os.path.join(fmap, 'T*Magnitude.nii.gz'))
# for fmapfile in fmap_files_list:
#     run = 1
#     fmap_file = os.path.split(fmapfile)[1]
#     filename_split = fmap_file.split('_')
#     acq = filename_split[2]
#     sub = filename_split[2]
#     run_number = filename_split[1][-1]
#     filename = 'sub-' + sub + '_' + 'run-0' + str(run) + '_magnitide'
#     FourDimImg(fmapfile, fmap, filename)
#     #looking into phasediff image
#     filename_phasediff = 'sub-' + sub + '_' + 'run-0' + str(run) + '_phasediff' + '.nii.gz'
#     filename_phasediff_path = os.path.join(fmap,filename_phasediff)
#     shutil.move(fmapfile.replace('Magnitude', 'Phase'), filename_phasediff_path)
#     filename_phasediff_json = filename_phasediff[:-6]+ 'json'
#     filename_phasediff_json_path = os.path.join(fmap, filename_phasediff_json)
#     touch(filename_phasediff_json_path)
#     intended_for_filename = 'anat/sub-' + sub + '_' + 'run-0' + run_number + '_' + filename_split[0] + '.nii.gz'
#     print('intended_for - ',intended_for_filename)
#     fmap_phasdiff_json_dict = {}
#     fmap_phasdiff_json_dict["intended_for"] = intended_for_filename
#     if filename_split[0] == 'T1w':
#         fmap_phasdiff_json_dict["EchoTime1"] = 0.00214
#         fmap_phasdiff_json_dict["EchoTime2"] = 0.00460
#     if filename_split[0] == 'T2w':
#         fmap_phasdiff_json_dict["EchoTime1"] = 0.00565
#         fmap_phasdiff_json_dict["EchoTime2"] = 0.00811
#     with open(filename_phasediff_json_path, 'w') as editfile:
#         json.dump( fmap_phasdiff_json_dict, editfile, indent = 4)

def FourDimImg(image, destinationpath_3d, outputfilename):
    #outputfilename= sub-285345_run-02_magnitude2
    img = ni.load(image)
    destination_path = destinationpath_3d
    images = ni.four_to_three(img)
    outputfilenamepattern = outputfilename + '{:01d}.nii.gz'
    for i, img_3d in enumerate(images):
        output_filename = outputfilenamepattern.format(i)
        output_path = os.path.join(destination_path, output_filename)
        ni.save(img_3d, output_path)









hcp2bids('/work/04275/suyashdb/lonestar/test_hcp/', '/work/04275/suyashdb/lonestar/test_output/')
