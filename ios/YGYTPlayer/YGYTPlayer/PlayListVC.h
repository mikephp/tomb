//
//  PlayListVC.h
//  YGYTPlayer
//
//  Created by dirlt on 15/11/12.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface PlayListVC : UITableViewController
// query data.
@property (nonatomic, strong) NSArray *languages;
@property (nonatomic, assign) NSInteger langIdx;
@property (nonatomic, strong) NSString *query;

// table view data.
@property (atomic, strong) NSMutableArray *data;
@property (nonatomic, assign) BOOL eof;

// refresh table view.
- (void) refresh;
@end
