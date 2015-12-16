//
//  HintCell.h
//  YGYTPlayer
//
//  Created by dirlt on 15/11/24.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface HintCell : UITableViewCell
+ (id) getInstance;
- (void) setHintText: (NSString*) text;
@end
