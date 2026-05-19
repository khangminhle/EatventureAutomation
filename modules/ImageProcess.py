import cv2
import numpy as np
from sklearn.cluster import DBSCAN

def resize_template(img, scale_x=1.0, scale_y=1.0):
    if(scale_x == 1 and scale_y == 1):
        return img

    return cv2.resize(img, None, fx=scale_x, fy=scale_y, interpolation=cv2.INTER_AREA)

def check_same_images(img1, img2):
    # Input img1, img2 BGR
    try:
        diff = cv2.absdiff(img1, img2)

        non_zero_count = np.count_nonzero(diff)

        if(non_zero_count == 0):
            print("The same image")
            return True
        else:
            print("Not the same image")
            return False
    except Exception as e:
        print("Error check_same_images:", e)
        
def find_points_match_template(img, template, threshold=0.8,check=False):
    # Đọc ảnh màn hình và ảnh icon
    w, h = template.shape[1], template.shape[0]

    # Thực hiện Template Matching
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    
    # Lấy tọa độ điểm khớp nhất
    #min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # Với CCOEFF_NORMED, max_loc là điểm bắt đầu của vùng khớp nhất
    #top_left = max_loc
    #bottom_right = (top_left[0] + w, top_left[1] + h)

    # Vẽ hình chữ nhật bao quanh kết quả
    #cv2.rectangle(img, top_left, bottom_right, 255, 2)
    #cv2.imwrite('Result.png', img)

    #print('Do chinh xac max:', max_val)
    #print('Do chinh xac min:', min_val)
    
    # Ngưỡng khớp (0.8 là khớp 80%)
    #threshold = 0.8
    #print(threshold)
    loc = np.where(res >= threshold)

    #print(res)

    if check:
        if(len(loc[0]) == 0):
            return False
        else:
            return True

    points = []
    for pt in zip(*loc[::-1]):
        # Tính toán tâm của biểu tượng
        center_x = pt[0] + w // 2
        center_y = pt[1] + h // 2
        points.append((center_x, center_y))
        #cv2.rectangle(img, (center_x-50, center_y-50), (center_x+50, center_y+50), 255, 2)

    #cv2.imwrite('Resutlts.png', img)
    if len(points)>0:
        points = clustering_centers(points)

    return points

def clustering_centers(raw_points, distance=20):
    """
    raw_points: Danh sách tọa độ thô [(x,y), (x,y)...] từ matchTemplate
    distance: Bán kính để gom cụm (pixel). Nút game thường cách nhau > 50px nên 20 là an toàn.
    """
    if not raw_points:
        return []

    # Chuyển dữ liệu sang dạng numpy array
    data = np.array(raw_points)

    # Khởi tạo DBSCAN
    # eps = distance: Khoảng cách tối đa giữa các điểm trong 1 cụm
    # min_samples = 1: Thấy 1 điểm cũng coi là cụm (để không bỏ sót nút nào)
    model = DBSCAN(eps=distance, min_samples=1).fit(data)

    labels = model.labels_
    centers = []

    # Duyệt qua từng cụm đã tìm được
    for label in set(labels):
        if label == -1: continue # Bỏ qua nhiễu
        
        # Lấy tất cả các điểm thuộc cụm hiện tại
        cluster_points = data[labels == label]
        
        # Tính toán tọa độ trung tâm (Average)
        center_x = int(np.mean(cluster_points[:, 0]))
        center_y = int(np.mean(cluster_points[:, 1]))
        
        centers.append((center_x, center_y))
        
    return centers