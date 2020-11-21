def files():
    save_all = open('./train_list.txt','a+')
    train = open('./video_name.txt', 'r')
    test = open('./test_list.txt', 'r')
    train_list = train.readlines()
    test_list = test.readlines()
    j = 0
    for i in train_list:
        if i not in test_list:
            save_all.writelines(i)
            j+= 1
    print(j)
if __name__=='__main__':
    files()
