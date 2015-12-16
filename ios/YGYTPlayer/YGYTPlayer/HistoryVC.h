//
//  HistoryVC.h
//  
//
//  Created by dirlt on 15/11/13.
//
//

#import <UIKit/UIKit.h>

@interface HistoryVC : UITableViewController
@property (atomic, strong) NSMutableArray *array;
- (void) reloadData;
@end
