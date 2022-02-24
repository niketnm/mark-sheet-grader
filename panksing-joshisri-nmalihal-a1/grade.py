import sys
import numpy as np
from PIL import Image
from PIL import ImageFilter


import sys


def get_coordinates(edges:np.array): 
    """
    edges : numpy array with edges detected
    returns:
    individual section coordinates (y), x-coordinates per question  
    """
    #saving the copy of edge numpy array as two different objects
    slice_1 = edges.copy()  
    slice_2 = edges.copy()
    

    ##Horizontal and vertical blobs
    for j in range(slice_1.shape[1]):
        if np.sum(slice_1[:,j]>10)>200:
            slice_1[:,j]=255
            
    for k in range(slice_2.shape[0]):
        if np.sum(slice_2[k,:]>10)>150:
            slice_2[k,:]=255
            
    #dilation and erosion on the resultant horizontal and verticle blobs   
    dilation_sec = Image.fromarray(np.uint8(slice_1),mode='L').filter(ImageFilter.MinFilter(3))
    dilation_sec_sl2 = Image.fromarray(np.uint8(slice_2),mode='L').filter(ImageFilter.MinFilter(3))
    dilation_sec = dilation_sec.filter(ImageFilter.MaxFilter(3))
    dilation_sec = dilation_sec.filter(ImageFilter.MaxFilter(3))
    dilation_sec_sl2 = dilation_sec_sl2.filter(ImageFilter.MaxFilter(3))
    dilation_sec_sl2 = dilation_sec_sl2.filter(ImageFilter.MaxFilter(3))



    #intersection of both to get the segregated boxes
    intersection = (np.asarray(dilation_sec)==255 ) * (np.asarray(dilation_sec_sl2)==255)
    #converting the output to PIL object
    output = Image.fromarray(np.uint8(intersection*255))
    #applying erosion to  properly segregate the boxes
    output =output.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MinFilter(7))
    
    #converted the image as numpy. Slicing the image below 600
    output_np = np.array(output)[600:]
    
    #Code below gets the top left x,y coordinates for the first section
    pixels = 30
    flag = False
    for i in range(0,output_np.shape[1]):

        for j in range(0, output_np.shape[0]):

            if output_np[j,i] ==255:
                flag=True
                start_index = (j,i)
                break
        if flag:
            break
            
    #Code below generates section y coordinates
    limit = 50
    coord = None
    c_list = []
    start = False
    for j in range(start_index[1],output_np.shape[1]):
        if output_np[start_index[0],j] == 255:
            limit = 50
            coord = (start_index[0],j)
            if start:
                c_list.append(coord)
                start=False
        else:
            limit-=1
        if limit==0:
            c_list.append(coord)
            limit = 50
            start = True
            
            
    indexes = sorted(np.array(list(set(c_list)))[:,1])
    
    
    
        
    
    row_index_to_start_with = 600 + start_index[0] - 3
    
    section_1_columns = (start_index[1]-55,indexes[0]+40)
    section_2_columns = (indexes[1]-55,indexes[2]+40)
    section_3_columns = (indexes[3]-55,indexes[4]+40)
    
    
    if len(indexes)<5:
        #if automatic slicing doesn;t work, we use the already known slicing 
        row_index_to_start_with = 675
        section_1_columns = (170,580)
        section_2_columns = (600,1010)
        section_3_columns = (1030,1440)
    
    #generating x coordinates for each question
    x_coords = []
    x_coords.append(start_index[0]+595)
    m = False
    q_counter = 28
    for i in range(start_index[0],output_np.shape[0]):
        if q_counter==0:
            break
        if output_np[i,start_index[1]] == 255:
            if m:
                x_coords.append(i+595)
                q_counter-=1
                m=False
        else:
            m=True
            
    
    return row_index_to_start_with,section_1_columns,section_2_columns,section_3_columns,x_coords        
    
    
def section_wise_answers(section:np.ndarray,thresholded_image:np.ndarray,coords,n_qstns = 29):
    
    result = []
    if len(coords)<29:
        coords = np.arange(675,len(section),47)
        offset = 47
    else:
        offset=47
#     for i in range(0,len(section),47):
#         sliced = section[i:i+47,:].copy()
         
#         im = thresholded_image[i:i+47,:].copy()
    max_qstns = n_qstns
    for xcoord in coords:

        #per question selected, row operations
        sliced = section[xcoord:xcoord+offset,:].copy()
        im = thresholded_image[xcoord:xcoord+offset,:].copy()
        
        if sliced.shape[0]<offset or np.sum(im)==0:
            # print("continued",xcoord)
            
            continue
        # plt.imshow(im)
        # plt.show()
        # plt.imshow(sliced)
        # plt.show() 
        #blob creation
        kernel = np.ones((sliced.shape[0],1))
        for j in range(sliced.shape[1]):
            if j==sliced.shape[1]-kernel.shape[1]+1:
                break
            product = kernel * sliced[:,j:j+kernel.shape[1]]
            if np.sum(np.sum(product==255,axis=0)>0):
                sliced[:,j]=255
                
        dilation = Image.fromarray(np.uint8(sliced),mode='L').filter(ImageFilter.MinFilter(3))
        dilation = dilation.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MaxFilter(3))
        dilation_np = np.asarray(dilation)

        # plt.imshow(dilation_np)
        # plt.show()
        
        #blob filtering
        flag = True
        blobs = []
        for k in range(dilation_np.shape[1]):

            if np.sum(dilation_np[:,k]==255)==offset and flag:
                start = k

                flag=False

            elif np.sum(dilation_np[:,k]==255)< offset and flag!=True:
                end = k
                flag = True
                blobs.append([start,end])

        c = 6    
        output = ""
        deleted_count = 0
        ans_mapping = {0:'x',1:"",2:"A",3:"B",4:"C",5:"D",6:"E"}
        for _,b in enumerate(blobs[::-1]):
            # print(np.sum(im[:,b[0]:b[1]]==255))
            if(np.sum(im[:,b[0]:b[1]]==255)) < 50:
                deleted_count+=1
                continue
            else:
            
                if np.sum(im[:,b[0]:b[1]])>120000 and c>=0:
                    output+=ans_mapping[c] 
            c-=1
        output = output[::-1]
        if len(blobs)-deleted_count >= 7:
            output = output + " " +ans_mapping[0] 

        if max_qstns==0:
            
            break
        result.append(output.strip())
        max_qstns-=1
        
    return result



if __name__ == '__main__':
    
    
    image_path = str(sys.argv[1])
    img = Image.open(image_path)
    
    #converting image to grayscale
    gray_img=img.convert('L')
    
    #applying edeg filter to the image
    edge = gray_img.filter(ImageFilter.FIND_EDGES)
    image_np =np.asarray(gray_img)
    
    
    #thresholding
    
    new_img = np.zeros(image_np.shape,dtype=float)
    new_img[image_np<5] =255
    
    edges_np = np.asarray(edge)
    
    coordinates = get_coordinates(edges_np)
    #slicing sections
    
    #sections below are for contour detection
    
    section_1 = edges_np[:,coordinates[1][0]:coordinates[1][1]].astype(float)
    section_2 = edges_np[:,coordinates[2][0]:coordinates[2][1]].astype(float)
    section_3 = edges_np[:,coordinates[3][0]:coordinates[3][1]].astype(float)
    
    #similar sections to above, used for answer detection
    new_img_sliced_1 = new_img[:,coordinates[1][0]:coordinates[1][1]].astype(float)
    new_img_sliced_2 = new_img[:,coordinates[2][0]:coordinates[2][1]].astype(float)
    new_img_sliced_3 = new_img[:,coordinates[3][0]:coordinates[3][1]].astype(float)
    
    
    # print(coordinates[4])
    
    file = open(str(sys.argv[2]), "w")
    
    for i,out in enumerate(section_wise_answers(section_1,new_img_sliced_1,coordinates[4]) + section_wise_answers(section_2,new_img_sliced_2,coordinates[4]) +section_wise_answers(section_3,new_img_sliced_3,coordinates[4],27)):
        file.write(str(i+1)+" "+ out+"\n")
        
    file.close()
    
    



        
    
    
    
    