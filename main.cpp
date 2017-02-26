#define _CRT_SECURE_NO_WARNINGS
#include <opencv2/core/core.hpp>
#include<opencv2/highgui/highgui.hpp>
#include<opencv2/imgproc/imgproc.hpp>
#include <tesseract/baseapi.h>
#include <leptonica/allheaders.h>
#include <iostream>
#include <string.h>
#include <ctype.h>
#include <vector>
using namespace std;
using namespace cv;
#define GRAY_THRESH 150
#define HOUGH_VOTE 100

class Receipt
{
    public:
        Receipt(string path)
        {
            m_path=path;
            flag=0;
        }
        void TiltCorrection()
        {
            Mat srcImg = imread(m_path,0);           //读取图片
            if (srcImg.rows*srcImg.cols>1000000)   //压缩
            {
                int t;
                if (srcImg.cols>srcImg.rows)t = 1000;
                        else t = 500;
                resize(srcImg, srcImg, Size(t, srcImg.rows*1.0 / srcImg.cols * t), 0, 0, CV_INTER_LINEAR);
            }
            Image=srcImg;
            //return srcImg;
            Point center(srcImg.cols / 2, srcImg.rows / 2);

            //Expand image to an optimal size, for faster processing speed
            //Set widths of borders in four directions
            //If borderType==BORDER_CONSTANT, fill the borders with (0,0,0)
            Mat padded;
            int opWidth = getOptimalDFTSize(srcImg.rows);
            int opHeight = getOptimalDFTSize(srcImg.cols);
            copyMakeBorder(srcImg, padded, 0, opWidth - srcImg.rows, 0, opHeight - srcImg.cols, BORDER_CONSTANT, Scalar::all(0));

            Mat planes[] = { Mat_<float>(padded), Mat::zeros(padded.size(), CV_32F) };
            Mat comImg;
            //Merge into a double-channel image
            merge(planes, 2, comImg);

            //Use the same image as input and output,
            //so that the results can fit in Mat well
            dft(comImg, comImg);

            //Compute the magnitude
            //planes[0]=Re(DFT(I)), planes[1]=Im(DFT(I))
            //magnitude=sqrt(Re^2+Im^2)
            split(comImg, planes);
            magnitude(planes[0], planes[1], planes[0]);

            //Switch to logarithmic scale, for better visual results
            //M2=log(1+M1)
            Mat magMat = planes[0];
            magMat += Scalar::all(1);
            log(magMat, magMat);

            //Crop the spectrum
            //Width and height of magMat should be even, so that they can be divided by 2
            //-2 is 11111110 in binary system, operator & make sure width and height are always even
            magMat = magMat(Rect(0, 0, magMat.cols & -2, magMat.rows & -2));

            //Rearrange the quadrants of Fourier image,
            //so that the origin is at the center of image,
            //and move the high frequency to the corners
            int cx = magMat.cols / 2;
            int cy = magMat.rows / 2;

            Mat q0(magMat, Rect(0, 0, cx, cy));
            Mat q1(magMat, Rect(0, cy, cx, cy));
            Mat q2(magMat, Rect(cx, cy, cx, cy));
            Mat q3(magMat, Rect(cx, 0, cx, cy));

            Mat tmp;
            q0.copyTo(tmp);
            q2.copyTo(q0);
            tmp.copyTo(q2);

            q1.copyTo(tmp);
            q3.copyTo(q1);
            tmp.copyTo(q3);

            //Normalize the magnitude to [0,1], then to[0,255]
            normalize(magMat, magMat, 0, 1, CV_MINMAX);
            Mat magImg(magMat.size(), CV_8UC1);
            magMat.convertTo(magImg, CV_8UC1, 255, 0);

            //Turn into binary image
            threshold(magImg, magImg, GRAY_THRESH, 255, CV_THRESH_BINARY);


            //Find lines with Hough Transformation
            vector<Vec2f> lines;
            float pi180 = (float)CV_PI / 180;
            Mat linImg(magImg.size(), CV_8UC3);
            HoughLines(magImg, lines, 1, pi180, HOUGH_VOTE, 0, 0);
            int numLines = lines.size();
            for (int l = 0; l<numLines; l++)
            {
                float rho = lines[l][0], theta = lines[l][1];
                Point pt1, pt2;
                double a = cos(theta), b = sin(theta);
                double x0 = a*rho, y0 = b*rho;
                pt1.x = cvRound(x0 + 1000 * (-b));
                pt1.y = cvRound(y0 + 1000 * (a));
                pt2.x = cvRound(x0 - 1000 * (-b));
                pt2.y = cvRound(y0 - 1000 * (a));
                line(linImg, pt1, pt2, Scalar(255, 0, 0), 3, 8, 0);
            }
            if (lines.size() == 3){
                cout << "found three angels:" << endl;
                cout << lines[0][1] * 180 / CV_PI << endl << lines[1][1] * 180 / CV_PI << endl << lines[2][1] * 180 / CV_PI << endl << endl;
            }
            //Find the proper angel from the three found angels
            float angel = 0;
            float piThresh = (float)CV_PI / 90;
            float pi2 = CV_PI / 2;
            for (int l = 0; l<numLines; l++)
            {
                float theta = lines[l][1];
                if (abs(theta) < piThresh || abs(theta - pi2) < piThresh)
                    continue;
                else{
                    angel = theta;
                    break;
                }
            }
            //Calculate the rotation angel
            //The image has to be square,
            //so that the rotation angel can be calculate right
            angel = angel<pi2 ? angel : angel - CV_PI;
            if (angel != pi2){
                float angelT = srcImg.rows*tan(angel) / srcImg.cols;
                angel = atan(angelT);
            }
            float angelD = angel * 180 / (float)CV_PI;
            cout << "the rotation angel to be applied:" << endl << angelD << endl << endl;
            //Rotate the image to recover
            Mat rotMat = getRotationMatrix2D(center, angelD, 1.0);
            Mat dstImg = Mat::ones(srcImg.size(), CV_8UC3);
            warpAffine(srcImg, dstImg, rotMat, srcImg.size(), 1, 0, Scalar(255, 255, 255));
            if (abs(angelD)<45.0)Image=dstImg;
        }

        void ProcessStr()
        {
            FILE* fp=fopen("temp","r");
            FILE* fp2=fopen("result","at");
            char s[1024],t1[100],t2[100];
            int flag1=12;
            while (!feof(fp)) {
                int cnt=0,cnt2=0;
                fgets(s,1024,fp);  //读取一行
                int len=strlen(s);
                if(len<8)continue;
                for(int i=len-1;i>=0&&cnt<flag1;i--)
                    if(s[i]>='0'&&s[i]<='9')t1[cnt++]=s[i];
                for(int i=cnt-1;i>=0;i--)t2[cnt2++]=t1[i];
                t2[cnt2]=0;
                if(cnt2==12)flag=(t2[0]=='1')?1:2,flag1=8;
                if(cnt2)fprintf(fp2,"%s\n", t2); //输出
            }
            fclose(fp);
            remove("temp");
            fclose(fp2);
        }

        void ocr(Mat data){
            char *outText;
            tesseract::TessBaseAPI *api = new tesseract::TessBaseAPI();
            // Initialize tesseract-ocr with English, without specifying tessdata path
            if (api->Init(NULL, "eng")) {
                fprintf(stderr, "Could not initialize tesseract.\n");
                exit(1);
            }
            api->SetPageSegMode(tesseract::PSM_SPARSE_TEXT_OSD);
            api->SetImage((uchar*)data.data, data.size().width, data.size().height, data.channels(), data.step1());
            // Get OCR result
            outText = api->GetUTF8Text();
            //printf("%s ",outText);
            api->Clear();
            api->End();
            FILE* fp=fopen("temp","w");
            fprintf(fp,"%s",outText);
            fclose(fp);
            ProcessStr();
        }

        void Img2b()                    //二值化
        {
            //threshold(Image, Image, 140, 255, THRESH_BINARY_INV);
            int blockSize = 25;
            int constValue = 10;
            cv::adaptiveThreshold(Image, Image, 255, CV_ADAPTIVE_THRESH_MEAN_C, CV_THRESH_BINARY_INV, blockSize, constValue);
            //imshow("二值化",Image);
        }

        void ProcessImage()
        {
            TiltCorrection();
            temp=Image.clone();
            Img2b();
            ocr(Image);
            imshow("发票",Image);
            //imwrite("temp.jpg", Image);
        }

        string type()
        {
            string s[3]={"无效","国税","地税"};
            return s[flag];
        }
    private:
        string m_path;
        Mat Image;
        Mat temp;
        int flag;
        vector<vector<Point> > contours;

};

void Output(string result)
{
    FILE * fp = fopen("result", "r");
    cout<<result<<endl;
    if(result=="无效")return ;
    char str[][20] = { "发票代码:", "发票号码:", "验证码:" },s[1024];
    int cnt=(result=="guoshui")?2:3,cnt1=0;
     while (!feof(fp)&&cnt1<cnt) {
            fgets(s,1024,fp);  //读取一行
            if(strlen(s)>0)printf("%s%s",str[cnt1++],s);
    }
    fclose(fp);
    remove("result");
}
int main(int argc, char* argv[])
{
	//string path = argv[1];
	string path ="test/6.jpg";
	Receipt receipt(path);
	receipt.ProcessImage();
	string result=receipt.type();
    Output(result);
	waitKey(0);
	destroyAllWindows();
	return 0;
}
