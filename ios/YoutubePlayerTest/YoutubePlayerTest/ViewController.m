//
//  ViewController.m
//  YoutubePlayerTest
//
//  Created by dirlt on 15/11/11.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import "ViewController.h"
#import <XCDYouTubeKit/XCDYouTubeKit.h>
#import <AVKit/AVKit.h>
#import <AVFoundation/AVFoundation.h>
#import <VKVideoPlayer/VKVideoPlayerViewController.h>
#import "YTPlayerVC.h"

@interface ViewController ()
@end

@implementation ViewController

// can not play https.
static NSString *HTTP_URL = @"http://7u2hx7.com1.z0.glb.clouddn.com/Peace.mp4";

- (void)viewDidLoad {
    [super viewDidLoad];
}
- (IBAction)playXCDVideo:(id)sender {
    XCDYouTubeVideoPlayerViewController *vc = [[XCDYouTubeVideoPlayerViewController alloc] initWithVideoIdentifier:@"oBu-pQG6sTY"];
    // video quality.
    vc.preferredVideoQualities =  @[@(XCDYouTubeVideoQualitySmall240), @(XCDYouTubeVideoQualityMedium360)];
    [self presentViewController:vc animated:YES completion:nil];
}


- (IBAction)playGoogleVideo:(id)sender {
    static NSString *videoId = @"oBu-pQG6sTY";
    YTPlayerVC* vc = [YTPlayerVC getInstance];
    [vc loadVideo:videoId];
    [self presentViewController:vc animated:YES completion:nil];
}

- (IBAction)playAVPlayer:(id)sender {
    AVPlayerViewController *vc = [[AVPlayerViewController alloc] init];
    vc.player = [AVPlayer playerWithURL:[NSURL URLWithString:HTTP_URL]];
    [self presentViewController:vc animated:YES completion:nil];
}

- (IBAction)playVKVideo:(id)sender {
    VKVideoPlayerViewController *vc = [[VKVideoPlayerViewController alloc] init];
    [self presentViewController:vc animated:YES completion:nil];
    [vc playVideoWithStreamURL:[NSURL URLWithString:HTTP_URL]];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

@end
