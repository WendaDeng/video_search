import spacy
import os

def Pos_split(cap_root):
    captions = os.path.join(caption_root,'train_caption.txt')
    cap_save = os.path.join(caption_root,'train_caption_nuon_remain.txt')
    cap_save = open(cap_save,'a+')
    captions = open(captions,'r').readlines()
    nlp_process = spacy.load('en')
    for cap in captions:
        noun_cap = []
        cap_remaining = []
        pos_result = nlp_process(cap.strip().split(' ',1)[1])
        pos_tags = {w:w.pos_ for w in pos_result}
        for w in pos_result:
            if w.pos_ == 'NOUN':
                noun_cap.append(str(w))
            else:
                cap_remaining.append(str(w))
        caption = cap.split(' ',1)[0]+' #Remaining# '+" ".join(cap_remaining)+' #NOUN# '+" ".join(noun_cap)+'\n'
        cap_save.write(caption)
        #assert len(cap.strip().split(' ')) == len(noun_cap) + len(cap_remaining) + 1
    print(len(captions))
 


if __name__ == '__main__':
    caption_root = '/mnt/cephfs/hhq/paper_file/dataset/FGAR_data/data/caption'
    Pos_split(caption_root)
