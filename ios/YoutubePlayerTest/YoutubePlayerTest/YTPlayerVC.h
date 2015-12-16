//
//  YTPlayerVC.h
//  YoutubePlayerTest
//
//  Created by dirlt on 15/11/19.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <YTPlayerView.h>

@interface YTPlayerVC : UIViewController<YTPlayerViewDelegate>
@property (nonatomic, strong) NSString *videoId;
+ (id) getInstance;
- (void) loadVideo: (NSString*) videoId;
@end
