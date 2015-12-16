//
//  YTPlayerVC.m
//  YoutubePlayerTest
//
//  Created by dirlt on 15/11/19.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import "YTPlayerVC.h"
#import "YTPlayerView.h"

@interface YTPlayerVC ()
@property (nonatomic, weak) IBOutlet YTPlayerView *playerView;
@end

@implementation YTPlayerVC

static YTPlayerVC *instance = nil;
+ (id) getInstance {
    if (instance) return instance;
    UIStoryboard *sb = [UIStoryboard storyboardWithName:@"Main" bundle:[NSBundle mainBundle]];
    instance = (YTPlayerVC*)[sb instantiateViewControllerWithIdentifier:@"GoogleVideo"];
    return instance;
}

- (void) loadVideo : (NSString*) videoId {
    self.videoId = videoId;
}

- (void)viewDidLoad {
    [super viewDidLoad];
    self.playerView.delegate = self;
    // Do any additional setup after loading the view.
}
- (void)viewDidAppear:(BOOL)animated {
    NSLog(@"video id = %@", self.videoId);
    [self.playerView loadWithVideoId:self.videoId];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

- (void)playerViewDidBecomeReady:(YTPlayerView *)playerView {
    NSLog(@"ready to play");
    [playerView seekToSeconds:10.0f allowSeekAhead:YES];
    [playerView playVideo];
}

/*
#pragma mark - Navigation

// In a storyboard-based application, you will often want to do a little preparation before navigation
- (void)prepareForSegue:(UIStoryboardSegue *)segue sender:(id)sender {
    // Get the new view controller using [segue destinationViewController].
    // Pass the selected object to the new view controller.
}
*/

@end
