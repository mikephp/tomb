//
//  VideoCell.h
//  
//
//  Created by dirlt on 15/11/16.
//
//

#import <UIKit/UIKit.h>

@interface VideoCell : UITableViewCell
+ (id) getInstance;
- (void) fillCell: (NSDictionary*) json;
- (CGFloat) rowHeight : (CGFloat) tableWidth;

@property (nonatomic, strong) NSDictionary *json;
@property (nonatomic, weak) IBOutlet UIImageView *coverImage;
@property (nonatomic, weak) IBOutlet UILabel *titleAndDesc;
@property (nonatomic, weak) IBOutlet UILabel *views;
@property (nonatomic, weak) IBOutlet UIImageView *viewIndicator;
@property (nonatomic, weak) IBOutlet UIButton *markButton;
@property (nonatomic, weak) IBOutlet UIView *V1;
@property (nonatomic, weak) IBOutlet UIView *V2;
@property (assign) BOOL hasMarked;
@end
