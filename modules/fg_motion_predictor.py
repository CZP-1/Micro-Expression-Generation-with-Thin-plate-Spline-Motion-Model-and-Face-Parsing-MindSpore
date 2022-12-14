from mindspore import  nn
import  mindspore
from mindspore.dataset.vision import  models

class FGMotionPredictor(nn.Module):
    """
    Module for foreground estimation, return single transformation, parametrized as 3x3 matrix. The third row is [0 0 1]
    """

    def __init__(self):
        super(FGMotionPredictor, self).__init__()
        self.bg_encoder = models.resnet18(pretrained=False)
        self.bg_encoder.conv1 = nn.Conv2d(6, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False)
        num_features = self.bg_encoder.fc.in_features
        self.bg_encoder.fc = nn.Linear(num_features, 8)
        self.bg_encoder.fc.weight.data.zero_()
        self.bg_encoder.fc.bias.data.copy_(mindspore.tensor([1, 0, 0, 0, 1, 0, 0, 0], dtype=mindspore.float))


    def forward(self, source_image, driving_image):
        bs = source_image.shape[0]
        out = mindspore.eye(3).unsqueeze(0).repeat(bs, 1, 1).type(source_image.type()) ## bs,3,3
        out = out.view(bs, -1)
        prediction = self.bg_encoder(mindspore.cat([source_image, driving_image], dim=1)) ## 两张图像放在一起求的仿射变换矩阵
        out[:,:8] = prediction
        out = out.view(bs, 3, 3)
        return out