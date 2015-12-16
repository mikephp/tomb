//
//  PlayerVC.m
//  YGYTPlayer
//
//  Created by dirlt on 15/11/19.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import "PlayerVC.h"
#import "YTPlayerView.h"
#import "RemoteDataSource.h"

@interface PlayerVC ()
@property (nonatomic, weak) IBOutlet YTPlayerView *playerView;
@property (nonatomic, strong) NSDictionary *json;
@property (nonatomic, strong) NSString *videoId;
@property (assign) NSInteger startSec;
@property (assign) BOOL played;
@end

@implementation PlayerVC

static PlayerVC *instance = nil;
+ (id) getInstance {
    if (instance) return instance;
    instance = (PlayerVC*)([[NSBundle mainBundle] loadNibNamed:@"PlayerVC" owner:nil options:nil][0]);
    instance.playerView.delegate = instance;
    return instance;
}

- (void)loadData:(NSDictionary*) json {
    self.json = json;
    self.videoId = json[@"id"];
    self.startSec = 0;
    self.played = NO;
}

- (void)viewDidLoad {
    [super viewDidLoad];
    // NSLog(@"PlayerVC did load");
    // Do any additional setup after loading the view from its nib.
}

- (void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];
    NSLog(@"video id = %@", self.videoId);
    // does not work.
    // [self.playerView cueVideoById:self.videoId startSeconds:self.startSec suggestedQuality:self.quality];
    // [self.playerView loadVideoById:self.videoId startSeconds:20 suggestedQuality:self.quality];
    RemoteDataSource *rds = [RemoteDataSource getInstance];
    __weak PlayerVC *me = self;
    [rds loadHistory:self.videoId withComplete:^(NSString *key, NSInteger elapse) {
        me.startSec = elapse;
        [me.playerView loadWithVideoId:me.videoId];
    }];
}

- (void) playerViewDidBecomeReady:(YTPlayerView *)playerView {
    // NSLog(@"video become ready");
    if (self.startSec) {
        [playerView seekToSeconds:self.startSec allowSeekAhead:YES];
    }
    [playerView playVideo];
    self.played = YES;
}

- (void)viewDidDisappear:(BOOL)animated {
    [super viewDidDisappear:animated];
    [self.playerView stopVideo];
    // if we don't play, we don't save elapse.
    if (self.played) {
        RemoteDataSource *rds = [RemoteDataSource getInstance];
        NSInteger elapse = (NSInteger)self.playerView.currentTime;
        if (elapse == 0) elapse = 1;
        [rds saveHistory:self.videoId withContent:self.json withElapse:elapse];
    }
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
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
