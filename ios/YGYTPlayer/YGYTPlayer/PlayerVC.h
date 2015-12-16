//
//  PlayerVC.h
//  YGYTPlayer
//
//  Created by dirlt on 15/11/19.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <YTPlayerView.h>

@interface PlayerVC : UIViewController<YTPlayerViewDelegate>
+ (id) getInstance;
- (void) loadData: (NSDictionary*)json;
@end
