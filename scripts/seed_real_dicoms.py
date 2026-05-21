#!/usr/bin/env python3
"""
Seed Orthanc with real DICOM studies for the Fanoni demo worklist.
- 7 studies covering MR, CT, CR, MG, US modalities
- CT and MRI studies have 30 slices with proper geometry for MPR/3D
- All studies use real pixel data (no empty shells)
"""

import copy
import io
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta
import random
import math

import pydicom
from pydicom.uid import generate_uid

ORTHANC = "http://localhost:8042"

SRC = {
    'MR':  '/Users/dafe/repos/fanoni-imaging/node_modules/dicomweb-client/testData/sample3.dcm',
    'US':  '/Users/dafe/repos/fanoni-imaging/node_modules/dicomweb-client/testData/US-PAL-8-10x-echo.dcm',
    'XA':  '/Users/dafe/repos/fanoni-imaging/node_modules/jpeg-lossless-decoder-js/tests/data/jpeg_lossless_sel1-8bit.dcm',
    'CR':  '/Users/dafe/repos/fanoni-imaging/node_modules/dicomweb-client/testData/sample2.dcm',
}

TODAY = datetime.now()

# Studies: list of (patient info, study info, list of series)
# Each series has slice_count — how many instances to create at different z-positions
STUDIES = [
    {
        'patient_id':   'FAN-001',
        'patient_name': 'Garcia^Maria^L',
        'dob':          '19680315',
        'sex':          'F',
        'accession':    'ACC-20250001',
        'description':  'Brain MRI w/ Contrast',
        'date_offset':  0,
        'priority':     'urgent',
        'series': [
            {
                'description': 'T1 Axial post-contrast',
                'modality':    'MR',
                'src':         'MR',
                'slices':      30,
                'orientation': 'axial',
                'pixel_spacing': [0.47, 0.47],
                'slice_thickness': 5.0,
            },
            {
                'description': 'T2 FLAIR Axial',
                'modality':    'MR',
                'src':         'MR',
                'slices':      30,
                'orientation': 'axial',
                'pixel_spacing': [0.47, 0.47],
                'slice_thickness': 5.0,
            },
            {
                'description': 'T1 Sagittal',
                'modality':    'MR',
                'src':         'MR',
                'slices':      20,
                'orientation': 'sagittal',
                'pixel_spacing': [0.47, 0.47],
                'slice_thickness': 5.0,
            },
        ],
    },
    {
        'patient_id':   'FAN-002',
        'patient_name': 'Lee^David^K',
        'dob':          '19550822',
        'sex':          'M',
        'accession':    'ACC-20250002',
        'description':  'CT Abdomen/Pelvis w/ Contrast',
        'date_offset':  -1,
        'priority':     'routine',
        'series': [
            {
                'description': 'Portal Venous Phase Abdomen',
                'modality':    'CT',
                'src':         'XA',
                'slices':      40,
                'orientation': 'axial',
                'pixel_spacing': [0.7, 0.7],
                'slice_thickness': 5.0,
            },
            {
                'description': 'Arterial Phase',
                'modality':    'CT',
                'src':         'XA',
                'slices':      40,
                'orientation': 'axial',
                'pixel_spacing': [0.7, 0.7],
                'slice_thickness': 5.0,
            },
        ],
    },
    {
        'patient_id':   'FAN-003',
        'patient_name': 'Johnson^Robert^A',
        'dob':          '19451110',
        'sex':          'M',
        'accession':    'ACC-20250003',
        'description':  'Chest X-Ray PA/Lateral',
        'date_offset':  0,
        'priority':     'routine',
        'series': [
            {
                'description': 'PA View',
                'modality':    'CR',
                'src':         'CR',
                'slices':      1,
                'orientation': 'axial',
                'pixel_spacing': [0.2, 0.2],
                'slice_thickness': 1.0,
            },
            {
                'description': 'Lateral View',
                'modality':    'CR',
                'src':         'CR',
                'slices':      1,
                'orientation': 'sagittal',
                'pixel_spacing': [0.2, 0.2],
                'slice_thickness': 1.0,
            },
        ],
    },
    {
        'patient_id':   'FAN-004',
        'patient_name': 'Davis^Emily^R',
        'dob':          '19900507',
        'sex':          'F',
        'accession':    'ACC-20250004',
        'description':  'Abdominal Ultrasound',
        'date_offset':  -2,
        'priority':     'routine',
        'series': [
            {
                'description': 'RUQ Survey',
                'modality':    'US',
                'src':         'US',
                'slices':      1,
                'orientation': 'axial',
                'pixel_spacing': [0.3, 0.3],
                'slice_thickness': 1.0,
            },
            {
                'description': 'Gallbladder Views',
                'modality':    'US',
                'src':         'US',
                'slices':      1,
                'orientation': 'axial',
                'pixel_spacing': [0.3, 0.3],
                'slice_thickness': 1.0,
            },
        ],
    },
    {
        'patient_id':   'FAN-005',
        'patient_name': 'Brown^Michael^T',
        'dob':          '19780214',
        'sex':          'M',
        'accession':    'ACC-20250005',
        'description':  'Right Knee MRI',
        'date_offset':  -3,
        'priority':     'routine',
        'series': [
            {
                'description': 'PD Fat Sat Sagittal',
                'modality':    'MR',
                'src':         'MR',
                'slices':      24,
                'orientation': 'sagittal',
                'pixel_spacing': [0.35, 0.35],
                'slice_thickness': 3.5,
            },
            {
                'description': 'T2 Coronal',
                'modality':    'MR',
                'src':         'MR',
                'slices':      24,
                'orientation': 'coronal',
                'pixel_spacing': [0.35, 0.35],
                'slice_thickness': 3.5,
            },
            {
                'description': 'T1 Axial',
                'modality':    'MR',
                'src':         'MR',
                'slices':      16,
                'orientation': 'axial',
                'pixel_spacing': [0.35, 0.35],
                'slice_thickness': 3.5,
            },
        ],
    },
    {
        'patient_id':   'FAN-006',
        'patient_name': 'Wilson^Jennifer^M',
        'dob':          '19620930',
        'sex':          'F',
        'accession':    'ACC-20250006',
        'description':  'Screening Mammogram',
        'date_offset':  -1,
        'priority':     'routine',
        'series': [
            {
                'description': 'Right CC',
                'modality':    'MG',
                'src':         'CR',
                'slices':      1,
                'orientation': 'axial',
                'pixel_spacing': [0.1, 0.1],
                'slice_thickness': 1.0,
            },
            {
                'description': 'Right MLO',
                'modality':    'MG',
                'src':         'CR',
                'slices':      1,
                'orientation': 'axial',
                'pixel_spacing': [0.1, 0.1],
                'slice_thickness': 1.0,
            },
            {
                'description': 'Left CC',
                'modality':    'MG',
                'src':         'CR',
                'slices':      1,
                'orientation': 'axial',
                'pixel_spacing': [0.1, 0.1],
                'slice_thickness': 1.0,
            },
            {
                'description': 'Left MLO',
                'modality':    'MG',
                'src':         'CR',
                'slices':      1,
                'orientation': 'axial',
                'pixel_spacing': [0.1, 0.1],
                'slice_thickness': 1.0,
            },
        ],
    },
    {
        'patient_id':   'FAN-007',
        'patient_name': 'Patel^Priya^S',
        'dob':          '19851220',
        'sex':          'F',
        'accession':    'ACC-20250007',
        'description':  'Left Shoulder X-Ray',
        'date_offset':  -4,
        'priority':     'routine',
        'series': [
            {
                'description': 'AP View',
                'modality':    'CR',
                'src':         'CR',
                'slices':      1,
                'orientation': 'axial',
                'pixel_spacing': [0.2, 0.2],
                'slice_thickness': 1.0,
            },
            {
                'description': 'Axillary Lateral View',
                'modality':    'CR',
                'src':         'CR',
                'slices':      1,
                'orientation': 'sagittal',
                'pixel_spacing': [0.2, 0.2],
                'slice_thickness': 1.0,
            },
        ],
    },
]


ORIENTATION_VECTORS = {
    'axial':    ([1.0, 0.0, 0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 1.0]),
    'sagittal': ([0.0, 1.0, 0.0, 0.0, 0.0, -1.0], [1.0, 0.0, 0.0]),
    'coronal':  ([1.0, 0.0, 0.0, 0.0, 0.0, -1.0], [0.0, 1.0, 0.0]),
}


def load_sources():
    return {k: pydicom.dcmread(v) for k, v in SRC.items()}


def make_instance(src_ds, study_meta, series_meta, study_uid, series_uid, instance_number, slice_index, total_slices):
    ds = copy.deepcopy(src_ds)

    study_date = (TODAY + timedelta(days=study_meta['date_offset'])).strftime('%Y%m%d')
    study_time = f"{random.randint(7,17):02d}{random.randint(0,59):02d}{random.randint(0,59):02d}"

    # Patient
    ds.PatientName = study_meta['patient_name']
    ds.PatientID = study_meta['patient_id']
    ds.PatientBirthDate = study_meta['dob']
    ds.PatientSex = study_meta['sex']

    # Study
    ds.StudyInstanceUID = study_uid
    ds.StudyDate = study_date
    ds.StudyTime = study_time
    ds.StudyDescription = study_meta['description']
    ds.AccessionNumber = study_meta['accession']
    ds.ReferringPhysicianName = 'Smith^John^P'
    ds.StudyID = f"S{study_meta['patient_id'][-3:]}"

    # Series
    ds.SeriesInstanceUID = series_uid
    ds.SeriesNumber = str(series_meta.get('_series_number', 1))
    ds.SeriesDescription = series_meta['description']
    ds.Modality = series_meta['modality']
    ds.SeriesDate = study_date
    ds.SeriesTime = study_time

    # Instance
    ds.SOPInstanceUID = generate_uid()
    ds.InstanceNumber = str(instance_number)

    # Spatial geometry for volumetric rendering
    orientation = series_meta.get('orientation', 'axial')
    iop, normal = ORIENTATION_VECTORS[orientation]
    pixel_spacing = series_meta.get('pixel_spacing', [1.0, 1.0])
    slice_thickness = series_meta.get('slice_thickness', 5.0)

    # Image center + slice offset along normal
    center_offset = (total_slices / 2.0) * slice_thickness
    z = slice_index * slice_thickness - center_offset
    ipp = [
        -128.0 * pixel_spacing[0] + normal[0] * z,
        -128.0 * pixel_spacing[1] + normal[1] * z,
        normal[2] * z,
    ]

    ds.ImageOrientationPatient = [f'{v:.6f}' for v in iop]
    ds.ImagePositionPatient = [f'{v:.6f}' for v in ipp]
    ds.SliceLocation = round(z, 4)
    ds.SliceThickness = str(slice_thickness)
    ds.PixelSpacing = [f'{pixel_spacing[0]:.6f}', f'{pixel_spacing[1]:.6f}']

    # Ensure file meta is correct
    if not hasattr(ds, 'file_meta') or ds.file_meta is None:
        from pydicom.dataset import FileMetaDataset
        ds.file_meta = FileMetaDataset()
    ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
    if hasattr(ds, 'SOPClassUID'):
        ds.file_meta.MediaStorageSOPClassUID = ds.SOPClassUID

    buf = io.BytesIO()
    pydicom.dcmwrite(buf, ds)
    return buf.getvalue()


def delete_all_studies():
    resp = urllib.request.urlopen(f'{ORTHANC}/studies')
    studies = json.loads(resp.read())
    print(f'Deleting {len(studies)} existing studies...')
    for sid in studies:
        req = urllib.request.Request(f'{ORTHANC}/studies/{sid}', method='DELETE')
        try:
            urllib.request.urlopen(req)
        except Exception:
            pass
    print('  done')


def upload_instance(dicom_bytes):
    req = urllib.request.Request(
        f'{ORTHANC}/instances',
        data=dicom_bytes,
        headers={'Content-Type': 'application/dicom'},
        method='POST',
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())


def main():
    print('=== Fanoni Imaging Demo Seed (Multi-Slice) ===\n')
    delete_all_studies()
    print()

    srcs = load_sources()
    results = []

    for study_meta in STUDIES:
        study_uid = generate_uid()
        print(f"Study: {study_meta['description']} — {study_meta['patient_name']}")

        orthanc_study_id = None
        total_instances = 0

        for si, series_meta in enumerate(study_meta['series']):
            series_meta = dict(series_meta)
            series_meta['_series_number'] = si + 1
            series_uid = generate_uid()
            n_slices = series_meta.get('slices', 1)
            src_key = series_meta['src']
            src_ds = srcs[src_key]

            for i in range(n_slices):
                dicom_bytes = make_instance(
                    src_ds, study_meta, series_meta,
                    study_uid, series_uid,
                    instance_number=i + 1,
                    slice_index=i,
                    total_slices=n_slices,
                )
                result = upload_instance(dicom_bytes)
                if orthanc_study_id is None:
                    orthanc_study_id = result.get('ParentStudy')
                total_instances += 1

            print(f"  Series {si+1}: {series_meta['description']:40s} {n_slices:3d} slices → OK")

        results.append({
            'orthanc_study_id': orthanc_study_id,
            'study_uid':   study_uid,
            'description': study_meta['description'],
            'patient':     study_meta['patient_name'],
            'priority':    study_meta['priority'],
            'instances':   total_instances,
        })
        print(f"  Orthanc: {orthanc_study_id} ({total_instances} instances total)")
        print()

    print('=== Summary ===')
    grand_total = 0
    for r in results:
        grand_total += r['instances']
        print(f"  {r['patient'][:25]:25s} | {r['description'][:35]:35s} | {r['priority']:7s} | {r['instances']:3d} instances")
    print(f"\nTotal: {len(results)} studies, {grand_total} instances")
    print('\nOpen OHIF at http://localhost:3000')
    print('Brain MRI MPR: http://localhost:3000/viewer?StudyInstanceUIDs=<uid>')


if __name__ == '__main__':
    main()
