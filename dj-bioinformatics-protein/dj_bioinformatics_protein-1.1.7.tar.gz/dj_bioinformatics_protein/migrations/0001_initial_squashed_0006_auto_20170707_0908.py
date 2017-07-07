# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-07 09:08
from __future__ import unicode_literals

import dj_bioinformatics_protein.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('dj_bioinformatics_protein', '0001_initial'), ('dj_bioinformatics_protein', '0002_remove_alignment_sha256'), ('dj_bioinformatics_protein', '0003_auto_20160227_0008'), ('dj_bioinformatics_protein', '0004_auto_20170621_1918'), ('dj_bioinformatics_protein', '0005_auto_20170627_2014'), ('dj_bioinformatics_protein', '0006_auto_20170707_0908')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alignment_method', models.CharField(choices=[('H', 'hhsearch'), ('S', 'sparksX'), ('U', 'user')], max_length=1)),
                ('rank', models.IntegerField()),
                ('active', models.BooleanField(default=True)),
                ('query_start', models.IntegerField()),
                ('query_aln_seq', dj_bioinformatics_protein.fields.AminoAcidAlignmentTextField(max_length=5000)),
                ('modified_query_aln_seq', dj_bioinformatics_protein.fields.AminoAcidAlignmentTextField(max_length=5000, null=True)),
                ('target_pdb_code', models.CharField(max_length=4)),
                ('target_pdb_chain', models.CharField(max_length=1)),
                ('target_start', models.IntegerField()),
                ('target_aln_seq', dj_bioinformatics_protein.fields.AminoAcidAlignmentTextField(max_length=5000)),
                ('modified_target_aln_seq', dj_bioinformatics_protein.fields.AminoAcidAlignmentTextField(max_length=5000, null=True)),
                ('p_correct', models.FloatField()),
                ('threaded_template', models.TextField(blank=True, null=True)),
                ('full_query_sequence', dj_bioinformatics_protein.fields.AminoAcidSequenceField(max_length=5000)),
                ('query_description', models.CharField(max_length=1000, null=True)),
                ('target_description', models.TextField(max_length=1000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FASTA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sha256', models.CharField(blank=True, editable=False, max_length=255, unique=True)),
                ('description', models.CharField(default='', max_length=1000)),
                ('comments', models.TextField(null=True)),
                ('sequence', dj_bioinformatics_protein.fields.AminoAcidSequenceField(max_length=5000)),
            ],
        ),
    ]
