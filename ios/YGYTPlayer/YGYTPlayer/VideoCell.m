//
//  VideoCell.m
//  
//
//  Created by dirlt on 15/11/16.
//
//

#import "VideoCell.h"
#import "RemoteDataSource.h"
#import "PlayListCell.h"
#import <YYWebImage/YYWebImage.h>

@implementation VideoCell

+ (id) getInstance {
    NSArray *nib = [[NSBundle mainBundle] loadNibNamed:@"VideoCell" owner:nil options:nil];
    VideoCell *cell = nib[0];
    cell.selectionStyle = UITableViewCellSelectionStyleNone;
    return cell;
}

- (CGFloat) rowHeight: (CGFloat) tableWidth {
    CGFloat width = tableWidth;
    // - 5 - 5 减去两边的margin
    // 360.0 / 480.0 是height / width比例
    // 100 是 titleAndDesc 高度
    // 50 是 stackview高度
    // 20 作为margin.
    CGFloat imageHeight = (width - 5 - 5) * 360.0 / 480.0;
    CGFloat margin = 15;
    return imageHeight + self.V1.frame.size.height + self.V2.frame.size.height + margin;
}

- (void) fillCell: (NSDictionary *)json {
    self.json = json;
    self.titleAndDesc.attributedText = [PlayListCell composeTitle:self.json[@"tt"] withDescription:self.json[@"desc"]];
    self.views.text = self.json[@"views"];
    // NSLog(@"hdim = %@", self.json[@"hdim"]);
    // [self.coverImage yy_setImageWithURL:[NSURL URLWithString:self.json[@"hdim"]] options:YYWebImageOptionProgressiveBlur | YYWebImageOptionSetImageWithFadeAnimation];
    [self.coverImage yy_setImageWithURL:[NSURL URLWithString:self.json[@"hdim"]] placeholder:[RemoteDataSource getInstance].placeholderImage options:YYWebImageOptionProgressiveBlur | YYWebImageOptionSetImageWithFadeAnimation completion:nil];
    __weak VideoCell *me = self;
    [[RemoteDataSource getInstance] loadBookMark:self.json[@"id"] withComplete:^(NSString *key, NSInteger mark) {
        self.hasMarked = mark;
        NSString *imgName = mark ? @"bookmark-512" : @"bookmark-empty-512";
        UIImage *img = [UIImage imageNamed:imgName];
        [me.markButton setImage:img forState:UIControlStateNormal];
    }];
}

- (void)awakeFromNib {
    // Initialization code
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
    [super setSelected:selected animated:animated];

    // Configure the view for the selected state
}

- (IBAction) markBooked:(id)sender {
    self.hasMarked = !self.hasMarked;
    UIImage *image = nil;
    if (self.hasMarked) image = [UIImage imageNamed:@"bookmark-512"];
    else image = [UIImage imageNamed:@"bookmark-empty-512"];
    [self.markButton setImage:image forState:UIControlStateNormal];
    [[RemoteDataSource getInstance] saveBookMark:self.json[@"id"] withContent:self.json withValue:self.hasMarked];
}

@end
