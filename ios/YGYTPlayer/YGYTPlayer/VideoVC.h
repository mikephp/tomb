//
//  VideoVC.h
//  YGYTPlayer
//
//  Created by dirlt on 15/11/12.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "VideoCell.h"

@interface VideoVC : UITableViewController
@property (nonatomic, strong) NSDictionary *json;
@property (atomic, strong) NSArray* videos;
@property (nonatomic, strong) VideoCell *header;
+ (id) getInstance;
- (void) loadData: (NSDictionary*) json;
@end
