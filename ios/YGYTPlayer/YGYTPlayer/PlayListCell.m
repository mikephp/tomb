
//
//  PlayListTableViewCell.m
//  YGYTPlayer
//
//  Created by dirlt on 15/11/12.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import "PlayListCell.h"
#import "RemoteDataSource.h"
#import <YYWebImage/YYWebImage.h>

@implementation PlayListCell

- (void)awakeFromNib {
    // Initialization code
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
    [super setSelected:selected animated:animated];

    // Configure the view for the selected state
}

+ (NSAttributedString*) composeTitle: (NSString*) title withDescription: (NSString*) desc {
    NSMutableAttributedString* s = [[NSMutableAttributedString alloc] initWithString:[NSString stringWithFormat:@"%@\n%@", title, desc]];
    [s addAttribute:NSFontAttributeName value:[UIFont boldSystemFontOfSize:14] range:NSMakeRange(0, title.length)];
    [s addAttribute:NSFontAttributeName value:[UIFont systemFontOfSize:12] range:NSMakeRange(title.length+1, desc.length)];
    return s;
}

+ (id) fetchCell: (UITableView*) tableView {
    PlayListCell *cell = [tableView dequeueReusableCellWithIdentifier:@"PlayListCell"];
    if (!cell) {
        NSArray *nib = [[NSBundle mainBundle] loadNibNamed:@"PlayListCell" owner:nil options:nil];
        cell = nib[0];
    }
    cell.histIndicator.hidden = YES;
    cell.markIndicator.hidden = YES;
    return cell;
}

+ (void) configureTableView:(UITableView *)tableView {
    // tableView.estimatedRowHeight = PLAY_LIST_CELL_HEIGHT;
    tableView.rowHeight = PLAY_LIST_CELL_HEIGHT;
}

- (void)fillWithDictionary:(NSDictionary *)json withCellKind:(PlayListCellKind)kind {
    NSString *title = json[@"tt"];
    NSString *desc = json[@"desc"];
    NSAttributedString *s = [PlayListCell composeTitle:title withDescription:desc];
    self.title.attributedText = s;
    self.views.text = json[@"views"];
    NSString *imageURL = json[@"hdim"];
    // NSLog(@"image url = %@", imageURL);
    // [self.image yy_setImageWithURL:[NSURL URLWithString:imageURL] options:YYWebImageOptionProgressiveBlur | YYWebImageOptionSetImageWithFadeAnimation];
    [self.image yy_setImageWithURL:[NSURL URLWithString:imageURL] placeholder:[RemoteDataSource getInstance].placeholderImage options:YYWebImageOptionProgressiveBlur | YYWebImageOptionSetImageWithFadeAnimation completion:nil];
    self.histIndicator.hidden = YES;
    self.markIndicator.hidden = YES;
    // self.viewIndicator.hidden = YES;
    __weak PlayListCell* me = self;
    if(kind == CELL_KIND_VIDEO) {
        [[RemoteDataSource getInstance] loadHistory:json[@"id"] withComplete:^(NSString *key, NSInteger elapse) {
            me.histIndicator.hidden = !elapse;
        }];
    }
}

@end
