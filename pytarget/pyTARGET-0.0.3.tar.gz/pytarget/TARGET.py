##################################################################
'''

TARGET - neTwork bAsed enRichment of Gene sETs

Author: Feng ZHANG - 2017-07-14

Email: 15110700005@fudan.edu.cn

'''
##################################################################


from  scipy import stats
import random
import numpy.ma as ma
import numpy as np
import multiprocessing


#One-side K-S test (scipy)
def ks_twosamp_greater(data1,data2):
    (data1, data2) = (ma.asarray(data1), ma.asarray(data2))
    (n1, n2) = (data1.count(), data2.count())
    n = (n1*n2/float(n1+n2))
    mix = ma.concatenate((data1.compressed(), data2.compressed()))
    mixsort = mix.argsort(kind='mergesort')
    csum = np.where(mixsort < n1, 1./n1, -1./n2).cumsum()
    if len(np.unique(mix)) < (n1+n2):
        csum = csum[np.r_[np.diff(mix[mixsort]).nonzero()[0],-1]]
    d = csum.max()
    prob = np.exp(-2*n*d**2)
    return prob




#STEP 1  Use network file and geneset file to generate the STEP files 
# network_path: path of network file/ col1 is gene, col2 is gene.
# geneset_path: path of gene set file. col1 is gene, col2 is gene set
# out_dir: directory of score files


def prepare_STEP(network_path, geneset_path, out_dir, max_step=3, PROC_LIMIT=10):

    #Get the confidence scores of gene pairs
    STRING={}
    STRING_WEIGHT={}
    GENE=set()
    fi=open(network_path)
    max_step=int(max_step)
    open(out_dir+'/max_step.info','w').write(str(max_step))
    for line in fi:
        seq=line.rstrip().split('\t')
        p1=seq[0]
        p2=seq[1]
        confidence = 1.0
        GENE.add(p1)
        GENE.add(p2)
        if len(seq) >=3:
            confidence = float(seq[2])

        if p1 in STRING:
            STRING[p1].add(p2)
            STRING_WEIGHT[p1][p2]=confidence
        else:
            STRING[p1]=set()
            STRING[p1].add(p2)
            STRING_WEIGHT[p1]={}
            STRING_WEIGHT[p1][p2]=confidence
        if p2 in STRING:
            STRING[p2].add(p1)
            STRING_WEIGHT[p2][p1]=confidence
        else:
            STRING[p2]=set()
            STRING[p2].add(p1)
            STRING_WEIGHT[p2]={}
            STRING_WEIGHT[p2][p1]=confidence
    fi.close()    

    fo=open(out_dir+'/gene.info','w')
    for gene in GENE:
        fo.write(gene+'\n')
    fo.close()

    #################################################

    go2gene={}
    gene2go={}
    fi=open(geneset_path)
    for line in fi:
        seq=line.rstrip().split('\t')
        gene=seq[0]
        go=seq[1]
        if go in go2gene:
            go2gene[go].add(gene)
        else:
            go2gene[go]=set([gene])
        if gene in gene2go:
            gene2go[gene].add(go)
        else:
            gene2go[gene]=set([go])

    fi.close()
    fo=open(out_dir+'/geneset.info','w')
    for go in go2gene:
        fo.write(go+'\n')
    fo.close()

    #############################################



    def get_STEP(go, GENE, go_genes, max_step, STRING, STRING_WEIGHT, out_dir):
        Step_result = {} 
        def STEP(gene, go, step):
            if step==0:
                step_tag =  gene+'_|_'+go+'_|_'+str(step)
                if gene in go_genes:
                    Step_result[step_tag] = [1.0, 1.0]
                else:
                    Step_result[step_tag] = [1.0, 0.0]
            else:
                step = step-1
                this_step_gene_list = STRING[gene]
                gene_in_go_num = 0
                if gene in go_genes:
                    gene_in_go_num=1
                gene_num = 1
                cof = 0.0
                for this_step_gene in this_step_gene_list:
                    cof += STRING_WEIGHT[gene][this_step_gene] 
                for this_step_gene in this_step_gene_list:
                    weight = STRING_WEIGHT[gene][this_step_gene]
                    step_tag = this_step_gene + '_|_' +go + '_|_' +str(step)
                    next_step = Step_result[step_tag]
                    gene_num += weight * next_step[0]/cof
                    gene_in_go_num += weight * next_step[1]/cof

                step_tag = gene+'_|_'+go+'_|_'+str(step+1) 
                Step_result[step_tag] = [gene_num, gene_in_go_num]

        step=0  
        
        while step <=max_step:
       
            for gene in GENE:
         
                STEP(gene, go, step)
            step +=1
        OUT={}

        for tag in Step_result:
            seq=tag.split('_|_')
            gene = seq[0]
            go = seq[1]   
            step = int(seq[2])
            score = Step_result[tag]
            if gene in OUT:
                OUT[gene][step]=str(score[0])+'|'+str(score[1])
            else:
                OUT[gene]=[]
                s=0
                while s <= max_step:
                    OUT[gene].append(0)
                    s+=1
                OUT[gene][step]=str(score[0])+'|'+str(score[1])
        fo=open(out_dir+'/'+go+'.score','w')
        for gene in GENE:
            fo.write(gene)
            step=0
            while step<=max_step:
                fo.write('\t'+str(OUT[gene][step]))
                step+=1
            fo.write('\n')
        fo.close()
    #########################################################################     
    jobs=[]  
    i=1 
    for go in go2gene:
        print "GENESET: "+str(i);i+=1
        go_genes=go2gene[go]
        ####################
        p=multiprocessing.Process(target=get_STEP, args=(go, GENE, go_genes, max_step, STRING, STRING_WEIGHT, out_dir))
        p.start()
        jobs.append(p)
        if len(jobs)>=PROC_LIMIT:
            for p in jobs:
                p.join()
            jobs=[]
    for p in jobs:
        p.join()
    ##############################################################################





#STEP 2  Generate the distribution of p-values used by the permutaion test
# score_dir: directory of score files
# LIST_LENGTH: the length gene list used by the permutation test
# LIMIT: the time of permutation test
# out_dir: directory of p-value distribution files

def prepare_DIST(score_dir, LIST_LENGTH, LIMIT, out_dir, seed=12345, PROC_LIMIT=10):
    random.seed(seed)
    LIMIT=int(LIMIT)
    GO = set()
    fi=open(score_dir+'/geneset.info')
    for line in fi:
        GO.add(line.rstrip())
    fi.close()
    GENE=set()
    fi=open(score_dir+'/gene.info')
    for line in fi:
        GENE.add(line.rstrip())
    fi.close()
    GENE_NUM=len(GENE)
    max_step = int(open(score_dir+'/max_step.info').read())

    open(out_dir+'/limit.info','w').write(str(LIMIT))
    open(out_dir+'/list_length.info','w').write(str(LIST_LENGTH))

    def Enrich(go,gene_list,SCORE,SCORE_GO_ALL,step,LIST_LENGTH):
        score_list=[]
        for gene in gene_list:
            score=0
            tag=gene+'|in|'+go
            if tag in SCORE:
                score=SCORE[tag]
            score_list.append(score)
        score_all = SCORE_GO_ALL[go]
        pv =float(ks_twosamp_greater(score_all,score_list))
        return pv



    def Permutation(RANDOM_LIST,go, LIMIT,SCORE,SCORE_GO_ALL,step,LIST_LENGTH,fo):
        PV_DIST=[]
        i=0
        while i < LIMIT:
            tmp_list= RANDOM_LIST[i]
            pv = Enrich(go, tmp_list,SCORE,SCORE_GO_ALL,step,LIST_LENGTH)
            PV_DIST.append(pv)
            i+=1
        PV_DIST.sort()
        for pv in PV_DIST:
            fo.write(str(pv)+'\n')
        fo.close()

    #########################################################
    SCORE_STEP={}
    for go in GO:
        SCORE_STEP[go]={}
        fi=open(score_dir+'/'+go+'.score')
        for line in fi:
            seq=line.rstrip().split('\t')
            gene=seq[0]
            score=[]            
            sc0= float(seq[1].split('|')[1])
            score.append(sc0)
            iii=2
            while iii <len(seq):
                sc =  float(seq[iii].split('|')[1])- float(seq[iii-1].split('|')[1])
                score.append(sc)
                iii+=1
            SCORE_STEP[go][gene]=score
    ############################################################
    step=0
    while step<=max_step:
        SCORE={}
        for go in SCORE_STEP:
            for gene in SCORE_STEP[go]:
                tag=gene+'|in|'+go
                SCORE[tag]=SCORE_STEP[go][gene][step]

        SCORE_GO_ALL={}
        for tag in SCORE:
            gene=tag.split('|in|')[0]
            go=tag.split('|in|')[1]
            score=SCORE[tag]
            if go in SCORE_GO_ALL:
                SCORE_GO_ALL[go].append(score)
            else:
                SCORE_GO_ALL[go]=[score]

        RANDOM_LIST=[]
        all_gene=[]
        for gene in GENE:
            all_gene.append(gene)
        PV_DIST=[]
        i=0
        while i<LIMIT:
            random.shuffle(all_gene)
            tmp_list=all_gene[:LIST_LENGTH]
            RANDOM_LIST.append(tmp_list)
            i+=1
        jobs=[]
        i=1
        for go in GO:
                print 'STEP: '+str(step)+'; gene set: '+ str(i);i+=1   
                fo=open(out_dir+'/'+go+'.'+str(step),'w')
                p= multiprocessing.Process(target=Permutation, args=(RANDOM_LIST,go, LIMIT,SCORE,SCORE_GO_ALL,step,LIST_LENGTH,fo))
                p.start()
                jobs.append(p)
                if len(jobs)>=PROC_LIMIT:
                    for p in jobs:
                        p.join()
                    jobs=[]
        for p in jobs:
            p.join()

        step +=1


#####################################################################################




#STEP 3  Enrichment
# score_dir: directory of score files
# dist_dir: directory of p-value distribution files
# genelist_path: path of genelist file
# out_dir: directory of output files


##################################################################
def enrich_MAIN(score_dir, dist_dir, genelist_path,  out_dir, PROC_LIMIT=10):

    GO = set()
    fi=open(score_dir+'/geneset.info')
    for line in fi:
        GO.add(line.rstrip())
    fi.close()
    GENE=set()
    fi=open(score_dir+'/gene.info')
    for line in fi:
        GENE.add(line.rstrip())
    fi.close()

    #########################################################
    SCORE_STEP={}
    for go in GO:
        SCORE_STEP[go]={}
        fi=open(score_dir+'/'+go+'.score')
        for line in fi:
            seq=line.rstrip().split('\t')
            gene=seq[0]
            score=[]
            sc0= float(seq[1].split('|')[1])
            score.append(sc0)
            iii=2
            while iii <len(seq):
                sc =  float(seq[iii].split('|')[1])- float(seq[iii-1].split('|')[1])
                score.append(sc)
                iii+=1
            SCORE_STEP[go][gene]=score
    ############################################################    
    fi = open(genelist_path)
    gene_list=[]
    old=set()
    for line in fi:
        seq=line.rstrip().split('\t')
        if seq[0] in GENE:
            if seq[0] not in old:
                gene_list.append(seq[0])
        old.add(seq[0])
    fi.close()
    ###########################################################
    max_step =  int(open(score_dir+'/max_step.info').read())
    LIMIT=float(open(dist_dir+'/limit.info').read())
    ##########################################################
    PV_DISTs={}
    iii=1
    for go in GO:
        PV_DISTs[go]=[]
        step=0
        while step<=max_step:
            print "prepare dist: STEP "+str(step)+'; GENESET '+str(iii);
            tmp=[]
            fi=open(dist_dir+'/'+go+'.'+str(step))
            for line in fi:
                tmp.append(float(line))
            fi.close()
            PV_DISTs[go].append(tmp)
            step+=1
        iii+=1
    ###################################
    def Enrich(score_all, score_list):

        pv = float(ks_twosamp_greater(score_all,score_list))

        return pv

    def enrich_step(go, SCORE_LIST, PV_DIST, SCORE_GO_ALL, max_step, LIMIT, fo):

        pvalue_list=[]
        step=0
        while step <= max_step:
            score_list = SCORE_LIST[step]
            score_all = SCORE_GO_ALL[step]
            pv = Enrich(score_all, score_list)
            pv_dist = PV_DIST[step]
            pv_rank_fw=LIMIT
            i=0
            while i < LIMIT:
                if pv < pv_dist[i]:
                    pv_rank_fw=i
                    break
                i+=1
            pv_rank= pv_rank_fw
            pv_new=min([max([pv_rank/float(LIMIT) , 1.0/10/float(LIMIT)]),1.0-1.0/10/float(LIMIT)])
            pvalue_list.append(pv_new)
            step += 1


        ############################################################################
        #combined_pvalue = stats.combine_pvalues( pvalue_list ,method='stouffer')[1]
        ##########################################################################
        pvalue_all=[]
        i=1
        while i<=LIMIT:
            pvalue_all.append(i/float(LIMIT))
            i+=1
        combined_pvalue = float(ks_twosamp_greater(pvalue_list,pvalue_all))
        ########################################################################


        fo.write('1\t'+str(go)+'\t'+str(combined_pvalue))
        for one in pvalue_list:
            fo.write('\t'+str(one))
        fo.write('\n')
        fo.close()

    #################################################################
    
    SCORE_GO_ALLs={}
    SCORE_LISTs={}
    i=1
    for go in GO:
        print "prepare geneset SCORE: "+str(i);i+=1
        SCORE_GO_ALLs[go]=[]
        SCORE_LISTs[go]=[]
        step=0
        while step<=max_step:
            SCORE_GO_ALLs[go].append([])
            SCORE_LISTs[go].append([])
            for gene in gene_list:
                SCORE_LISTs[go][step].append(SCORE_STEP[go][gene][step])
            for gene in GENE:
                SCORE_GO_ALLs[go][step].append(SCORE_STEP[go][gene][step])
            step+=1

    jobs=[]
    i=1
    for go in GO:
        print "ENRICH GENESET: "+str(i);i+=1
        fo=open(out_dir+'/'+go+'.enrich','w')
        PV_DIST=PV_DISTs[go]
        SCORE_LIST=SCORE_LISTs[go]
        SCORE_GO_ALL=SCORE_GO_ALLs[go]
        p= multiprocessing.Process(target=enrich_step, args=(go, SCORE_LIST, PV_DIST, SCORE_GO_ALL, max_step, LIMIT, fo))
        p.start()
        jobs.append(p)
        if len(jobs)>=PROC_LIMIT:
            for p in jobs:
                p.join()
            jobs=[]
    for p in jobs:
        p.join()

    

