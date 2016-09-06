//显示图像文件
#include <opencv2/opencv.hpp>
using namespace std;

    

IplImage *pImage;
//IplImage *pCannyImage;
IplImage *pGrayImage;
IplImage *pBinaryImage;

const char *pstrWindowsAfterTitle = "After";

//cvCreateTrackbar的回调函数
void on_trackbar(int threshold)
{
//    //canny边缘检测
//    cvCanny(pImage, pCannyImage, threshold, threshold * 3, 3);
//    cvShowImage(pstrWindowsCannyTitle, pCannyImage);
    
    //转为二值图
    cvThreshold(pGrayImage, pBinaryImage,threshold , 255, CV_THRESH_BINARY);
    cvShowImage(pstrWindowsAfterTitle, pBinaryImage);
}



int main()
{
    const char *pstrImageName = "1.jpg";
    
    const char *pstrWindowsSrcTitile = "origin";
    const char *pstrWindowsToolBar = "Threshold";
    
    IplImage *pImage = cvLoadImage(pstrImageName,CV_LOAD_IMAGE_UNCHANGED);
    cvNamedWindow(pstrWindowsSrcTitile,CV_WINDOW_AUTOSIZE);
    
  
    /*二值图
    //转为灰度图
    pGrayImage = cvCreateImage(cvGetSize(pImage), IPL_DEPTH_8U, 1);
    cvCvtColor(pImage, pGrayImage, CV_BGR2GRAY);
    //创建二值图
    pBinaryImage = cvCreateImage(cvGetSize(pGrayImage), IPL_DEPTH_8U, 1);
    cvNamedWindow(pstrWindowsAfterTitle,CV_WINDOW_AUTOSIZE);
    cvShowImage(pstrWindowsSrcTitile, pImage);
    
    int nThreshold = 0;
    cvCreateTrackbar(pstrWindowsToolBar, pstrWindowsAfterTitle, &nThreshold, 254, on_trackbar);
    
    on_trackbar(1);
     
     */
    
    
    /*canny边缘检测
    pCannyImage = cvCreateImage(cvGetSize(pImage), IPL_DEPTH_8U, 1);
    cvNamedWindow(pstrWindowsCannyTitle,CV_WINDOW_AUTOSIZE);
    
    int nThresHoldEdge = 1;
    cvCreateTrackbar(pstrWindowsToolBar, pstrWindowsCannyTitle, &nThresHoldEdge, 100,on_trackbar);
    
    on_trackbar(1);
    
     */
    
    /*  图像缩放
    double fScale = 0.314; //缩放倍数
    CvSize cvSize;  //目标图像尺寸
    
    //计算目标图像大小
    cvSize.width = pImage->width * fScale;
    cvSize.height = pImage->height * fScale;
    
    //创建图像并缩放
    pDstImage = cvCreateImage(cvSize, pImage->depth, pImage->nChannels);
    cvResize(pImage, pDstImage,CV_INTER_AREA);
    
     */
   
    //等待按键事件
    cvWaitKey(0);
    
    //保存图片
//    cvSaveImage(pstrSaveImageName, pDstImage);
    
    cvDestroyWindow(pstrWindowsSrcTitile);
//    cvDestroyWindow(pstrWindowsDstTitle);
    cvReleaseImage(&pImage);
//    cvReleaseImage(&pDstImage);
    return 0;
}
