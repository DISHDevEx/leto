from super_image import PanModel, ImageLoader
from PIL import Image
import requests

def parse_args():
    """
    Parses the arguments needed for Super Resolution reconstruction module.
    Catalogues: input s3 bucket, input s3 prefix, output s3 bucket, output s3 prefix,
            codec, resolution, model bucket, model prefix and algorithm.

    Returns
    -------
        args: argparse.Namespace object
            Returns an object with the relevent input s3 bucket, input s3 prefix, output s3 bucket,
            output s3 prefix, codec, resolution, model bucket, model prefix and algorithm.
    """

    parser = argparse.ArgumentParser(description="Inference script of opencv video upscaler")

    parser.add_argument('--input_bucket_s3',
                        type =str,
                        help ='s3 bucket of the input video',
                        default = "leto-dish")

    parser.add_argument("--input_prefix_s3",
                        type = str,
                        help = "s3 prefix of the input video",
                        default = 'reduced-videos/benchmark/ffmpeg-resolution-downsampler/car/')

    parser.add_argument("--output_bucket_s3",
                        type=str,
                        default = "leto-dish",
                        help = "s3 bucket of the output video")

    parser.add_argument("--output_prefix_s3",
                        type = str,
                        default = "reconstructed-videos/benchmark/superres/car/",
                        help ="s3 prefix of the output video")

    parser.add_argument("--temp_path",
                        type = str,
                        default = 'temp',
                        help ="A temp folder to store video from uploading to s3")

    parser.add_argument("--quality",
                        type = int,
                        default = 15,
                        help="The compression rate for cv2 to apply, 100 is for best video quality, 0 is for the worse video quality ")

    args = parser.parse_args()

    return args

def pan_sr(video, model , path):
    #apply pan sr here for each video



def main():
    args = parse_args()
    aux = Aux()


    model = PanModel.from_pretrained("eugenesiow/pan", scale =2)
    puts = ImageLoader.load_image(image)
    preds = model(inputs)

    ImageLoader.save_image(preds, "2x.png")

    !static_ffmpeg -framerate 25 -pattern_type glob -i 'frames/*.jpg' -crf 28 -preset slow -c:v libx264 pan_4x.mp4


    os.mkdir('./temp')


    video_list  = aux.load_s3(args.input_bucket_s3, args.input_prefix_s3)
    for video in video_list:
        cv2_jpg_compress(video)

    result = aux.load_local("temp/", args.output_bucket_s3, args.output_prefix_s3)

    aux.upload_s3(result)


if __name__ == "__main__":
    main()
