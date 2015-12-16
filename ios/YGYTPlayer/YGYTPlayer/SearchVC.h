//
//  FilterVC.h
//  YGYTPlayer
//
//  Created by dirlt on 15/11/13.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "PlayListVC.h"

@interface SearchVC : UITableViewController<UISearchBarDelegate, UISearchControllerDelegate, UISearchResultsUpdating>
@property (nonatomic, weak) PlayListVC *rootVC;
@property (nonatomic, weak) NSArray *languages;
+ (id) getInstance;
- (void) loadData: (PlayListVC*) rootVC;
@end

