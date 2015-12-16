//
//  PlayListTableViewCell.h
//  YGYTPlayer
//
//  Created by dirlt on 15/11/12.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import <UIKit/UIKit.h>

static const int PLAY_LIST_CELL_HEIGHT = 100;

@interface PlayListCell : UITableViewCell
@property (nonatomic, weak) IBOutlet UILabel* title;
@property (nonatomic, weak) IBOutlet UIImageView* image;
@property (nonatomic, weak) IBOutlet UILabel* views;
@property (nonatomic, weak) IBOutlet UIImageView* viewIndicator;
@property (nonatomic, weak) IBOutlet UIImageView* histIndicator;
@property (nonatomic, weak) IBOutlet UIImageView* markIndicator;

typedef NS_ENUM(NSInteger, PlayListCellKind) {
    CELL_KIND_PLAYLIST,
    CELL_KIND_HISTORY,
    CELL_KIND_BOOKMARK,
    CELL_KIND_VIDEO,
};
- (void) fillWithDictionary: (NSDictionary*) json withCellKind: (PlayListCellKind) kind;
+ (NSAttributedString*) composeTitle: (NSString*) title withDescription: (NSString*) desc;
+ (id) fetchCell: (UITableView*) tableView;
+ (void) configureTableView: (UITableView*) tableView;
@end
