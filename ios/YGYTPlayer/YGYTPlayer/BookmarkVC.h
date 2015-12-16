//
//  BookmarkVC.h
//  YGYTPlayer
//
//  Created by dirlt on 15/11/13.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface BookmarkVC : UITableViewController
@property (atomic, strong) NSMutableArray* array;
- (void) reloadData;
@end
